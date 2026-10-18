// Stopwatch top level for the DE10-Lite
//
// Switches (active high):
//   SW0 = go      (raise to start from idle, rising edge)
//   SW1 = pause   (hold up to pause, drop to resume)
//   SW2 = lap     (raise while running to capture a lap)
//   SW3 = stop    (while paused, raise to stop and clear everything)
//   SW9 = display select (0 = live count, 1 = stored lap)
//
// KEY0 = reset (active low button)
//
// Display: HEX3 HEX2 . HEX1 HEX0  ->  SS.hh  (when TICK_DIV = 500_000)
//   For a 1 Hz bring-up test, set TICK_DIV = 50_000_000 and SHOW_DP = 0.
//
// Requires FSM_STOPWATCH, FSM_STOPWATCH_DATAPATH and tick_gen in the project.

module TOP_LVL #(
    parameter int TICK_DIV = 500_000,   // 50 MHz / 500_000 = 100 Hz (10 ms per count)
    parameter bit SHOW_DP  = 1'b1       // decimal point on HEX2
)(
    input  logic       MAX10_CLK1_50,
    input  logic [1:0] KEY,
    input  logic [9:0] SW,
    output logic [7:0] HEX0,
    output logic [7:0] HEX1,
    output logic [7:0] HEX2,
    output logic [7:0] HEX3,
    output logic [7:0] HEX4,
    output logic [7:0] HEX5
);

    logic clk;
    logic rst;

    assign clk = MAX10_CLK1_50;
    assign rst = ~KEY[0];                // KEY is active low

    // ------------------------------------------------------------
    // 2-FF synchronizers for the asynchronous switches
    // ------------------------------------------------------------
    logic [4:0] sw_meta, sw_sync;

    always_ff @(posedge clk) begin
        sw_meta <= {SW[9], SW[3:0]};
        sw_sync <= sw_meta;
    end

    logic go, pause, lap, stop, show_lap;

    assign go       = sw_sync[0];
    assign pause    = sw_sync[1];
    assign lap      = sw_sync[2];
    assign stop     = sw_sync[3];
    assign show_lap = sw_sync[4];

    // ------------------------------------------------------------
    // Tick generator, FSM, datapath
    // ------------------------------------------------------------
    logic tick;
    logic run_en, lap_en, stop_sel;
    logic [15:0] count, lap_count;

    tick_gen #(
        .DIV(TICK_DIV)
    ) u_tick (
        .clk (clk),
        .rst (rst),
        .tick(tick)
    );

    FSM_STOPWATCH u_fsm (
        .clk     (clk),
        .rst     (rst),
        .go      (go),
        .pause   (pause),
        .lap     (lap),
        .stop    (stop),
        .run_en  (run_en),
        .lap_en  (lap_en),
        .stop_sel(stop_sel)
    );

    FSM_STOPWATCH_DATAPATH #(
        .WIDTH(16),
        .MAX  (9999)
    ) u_dp (
        .clk      (clk),
        .rst      (rst),
        .tick     (tick),
        .run_en   (run_en),
        .lap_en   (lap_en),
        .stop_sel (stop_sel),
        .count    (count),
        .lap_count(lap_count)
    );

    // ------------------------------------------------------------
    // Display select and digit split
    // ------------------------------------------------------------
    logic [15:0] disp_val;
    logic [3:0]  d0, d1, d2, d3;

    assign disp_val = show_lap ? lap_count : count;

    always_comb begin
        d0 = 4'(disp_val % 10);
        d1 = 4'((disp_val / 10) % 10);
        d2 = 4'((disp_val / 100) % 10);
        d3 = 4'((disp_val / 1000) % 10);
    end

    // ------------------------------------------------------------
    // 7-segment decoder (active low, bits = {g,f,e,d,c,b,a})
    // ------------------------------------------------------------
    function automatic logic [6:0] seg7(input logic [3:0] d);
        case (d)
            4'd0:    seg7 = 7'b1000000;
            4'd1:    seg7 = 7'b1111001;
            4'd2:    seg7 = 7'b0100100;
            4'd3:    seg7 = 7'b0110000;
            4'd4:    seg7 = 7'b0011001;
            4'd5:    seg7 = 7'b0010010;
            4'd6:    seg7 = 7'b0000010;
            4'd7:    seg7 = 7'b1111000;
            4'd8:    seg7 = 7'b0000000;
            4'd9:    seg7 = 7'b0010000;
            default: seg7 = 7'b1111111;
        endcase
    endfunction

    // Bit 7 is the decimal point (active low, 1 = off)
    assign HEX0 = {1'b1,       seg7(d0)};
    assign HEX1 = {1'b1,       seg7(d1)};
    assign HEX2 = {~SHOW_DP,   seg7(d2)};
    assign HEX3 = {1'b1,       seg7(d3)};
    assign HEX4 = 8'hFF;       // off
    assign HEX5 = 8'hFF;       // off

endmodule