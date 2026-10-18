module CALC #(
    parameter WIDTH = 3
)
(
    input  logic             clk,
    input  logic             rst,
    input  logic [WIDTH-1:0] in1,
    input  logic [WIDTH-1:0] in2,
    output logic [WIDTH:0]   op_out,
    input  logic             add_en,
    input  logic             sub_en,
    input  logic             mult_en,
    input  logic             div_en
);

    typedef enum logic [2:0] {
        START,
        ADD,
        SUB,
        MULT,
        DIV
    } state_t;

    state_t c_state, n_state;

    // State register
    always_ff @(posedge clk) begin
        if (rst) begin
            c_state <= START;
        end
        else begin
            c_state <= n_state;
        end
    end

    // Next-state logic and outputs
    always_comb begin
        n_state = c_state;
        op_out  = '0;

        case (c_state)
            START: begin
                if (add_en)  n_state = ADD;
                if (sub_en)  n_state = SUB;
                if (mult_en) n_state = MULT;
                if (div_en)  n_state = DIV;
            end

            ADD: begin
                op_out  = in1 + in2;
                n_state = START;
            end

            SUB: begin
                op_out  = in1 - in2;
                n_state = START;
            end

            MULT: begin
                op_out  = in1 << 1;
                n_state = START;
            end

            DIV: begin
                op_out  = in1 >> 1;
                n_state = START;
            end

            default: begin
                n_state = START;
            end
        endcase
    end

endmodule