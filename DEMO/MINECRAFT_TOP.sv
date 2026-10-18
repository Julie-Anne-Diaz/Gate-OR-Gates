// Minecraft I/O adapter for the stopwatch. The original FPGA top is unchanged.
// HEX0..HEX3 are binary digits consumed by the SEVENSEG_HEX block component.
module MINECRAFT_TOP #(
    parameter integer TICK_DIV = 1
)(
    input logic clk, rst, go, pause, lap, stop, show_lap,
    output logic [3:0] HEX0, HEX1, HEX2, HEX3
);
    logic [4:0] sw_meta, sw_sync;
    always_ff @(posedge clk) begin
        sw_meta <= {show_lap, stop, lap, pause, go};
        sw_sync <= sw_meta;
    end

    logic tick, run_en, lap_en, stop_sel;
    // 14 bits represent every reachable count (0..9999); the FPGA top uses 16.
    logic [13:0] count, lap_count, disp_val;
    generate
        if (TICK_DIV == 1) begin : every_cycle
            assign tick = 1'b1;
        end else begin : divided_clock
            tick_gen #(.DIV(TICK_DIV)) u_tick (.clk(clk), .rst(rst), .tick(tick));
        end
    endgenerate
    FSM_STOPWATCH u_fsm (
        .clk(clk), .rst(rst), .go(sw_sync[0]), .pause(sw_sync[1]),
        .lap(sw_sync[2]), .stop(sw_sync[3]),
        .run_en(run_en), .lap_en(lap_en), .stop_sel(stop_sel)
    );
    FSM_STOPWATCH_DATAPATH #(.WIDTH(14), .MAX(9999)) u_dp (
        .clk(clk), .rst(rst), .tick(tick), .run_en(run_en),
        .lap_en(lap_en), .stop_sel(stop_sel), .count(count), .lap_count(lap_count)
    );
    assign disp_val = sw_sync[4] ? lap_count : count;
    BINARY14_TO_BCD u_digits(.value(disp_val), .digits({HEX3,HEX2,HEX1,HEX0}));
endmodule

module BINARY14_TO_BCD(input logic [13:0] value, output logic [15:0] digits);
    // Shift/add-3 binary-to-BCD avoids synthesizing general division networks.
    // Discarding the ten-thousands digit matches the FPGA's four decimal digits
    // even for values above the normal 0..9999 counter range.
    logic [15:0] bcd;
    always_comb begin
        bcd = '0;
        for (integer bit_index = 13; bit_index >= 0; bit_index = bit_index - 1) begin
            for (integer digit = 0; digit < 4; digit = digit + 1)
                if (bcd[4*digit +: 4] >= 5)
                    bcd[4*digit +: 4] = bcd[4*digit +: 4] + 4'd3;
            bcd = {bcd[14:0], value[bit_index]};
        end
        digits = bcd;
    end
endmodule
