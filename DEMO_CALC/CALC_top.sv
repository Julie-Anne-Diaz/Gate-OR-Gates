// Top level for FSM_CALC on the Terasic DE10-Lite (active-low keys and segments)
//
//   KEY[0]    : manual clock (press = one clock edge)
//   KEY[1]    : reset
//   SW[9]     : add_en
//   SW[8]     : sub_en
//   SW[7]     : mult_en  (in1 * 2)
//   SW[6]     : div_en   (in1 / 2)
//   SW[5:3]   : in1
//   SW[2:0]   : in2
//
//   HEX3      : in1
//   HEX2      : in2
//   HEX1,HEX0 : result in decimal (HEX1 shows "-" for a negative subtract
//               result, or the tens digit 1 for results 10..14)
//   LEDR[3:0] : raw op_out bits

module CALC_top (
    input  logic       MAX10_CLK1_50,   // unused, kept so the pin assignments can stay
    input  logic [1:0] KEY,
    input  logic [9:0] SW,
    output logic [7:0] HEX0,
    output logic [7:0] HEX1,
    output logic [7:0] HEX2,
    output logic [7:0] HEX3,
    output logic [7:0] HEX4,
    output logic [7:0] HEX5,
    output logic [9:0] LEDR
);

    localparam WIDTH = 3;

    logic             clk, rst;
    logic [WIDTH-1:0] in1, in2;
    logic [WIDTH:0]   op_out;
    logic             add_en, sub_en, mult_en, div_en;

    assign clk     = ~KEY[0];   // keys are active low -> rising edge on press
    assign rst     = ~KEY[1];

    assign add_en  = SW[9];
    assign sub_en  = SW[8];
    assign mult_en = SW[7];
    assign div_en  = SW[6];

    assign in1     = SW[5:3];
    assign in2     = SW[2:0];

    CALC #(.WIDTH(WIDTH)) u_calc (
        .clk     (clk),
        .rst     (rst),
        .in1     (in1),
        .in2     (in2),
        .op_out  (op_out),
        .add_en  (add_en),
        .sub_en  (sub_en),
        .mult_en (mult_en),
        .div_en  (div_en)
    );

    // ---------- Result formatting ----------
    // The FSM gives priority div > mult > sub > add when several enables are on,
    // so a result is a signed subtract only when sub is the winning operation.
    logic       is_sub, neg;
    logic [3:0] mag, tens, ones;

    assign is_sub = sub_en & ~mult_en & ~div_en;
    assign neg    = is_sub & op_out[WIDTH];                 // borrow bit = negative
    assign mag    = neg ? (~op_out + 4'd1) : op_out;        // magnitude, 0..14
    assign tens   = (mag >= 4'd10) ? 4'd1 : 4'd0;
    assign ones   = (mag >= 4'd10) ? (mag - 4'd10) : mag;

    // ---------- 7-seg decoder (active low) ----------
    // Segment order: {dp, g, f, e, d, c, b, a}
    function automatic logic [7:0] seg_digit(input logic [3:0] d);
        case (d)
            4'd0: return 8'b1100_0000;
            4'd1: return 8'b1111_1001;
            4'd2: return 8'b1010_0100;
            4'd3: return 8'b1011_0000;
            4'd4: return 8'b1001_1001;
            4'd5: return 8'b1001_0010;
            4'd6: return 8'b1000_0010;
            4'd7: return 8'b1111_1000;
            4'd8: return 8'b1000_0000;
            4'd9: return 8'b1001_0000;
            default: return 8'hFF;
        endcase
    endfunction

    localparam logic [7:0] SEG_MINUS = 8'b1011_1111;  // only segment g on
    localparam logic [7:0] SEG_BLANK = 8'hFF;

    assign HEX3 = seg_digit({1'b0, in1});
    assign HEX2 = seg_digit({1'b0, in2});

    // HEX1: "-" if negative, "1" for 10..14, otherwise blank
    assign HEX1 = neg          ? SEG_MINUS :
                  (tens != 0)  ? seg_digit(tens) : SEG_BLANK;
    assign HEX0 = seg_digit(ones);

    assign HEX4 = SEG_BLANK;
    assign HEX5 = SEG_BLANK;

    assign LEDR = {6'b0, op_out};

endmodule