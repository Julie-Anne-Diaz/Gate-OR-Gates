
`timescale 1ns/1ps

// Abhiram Pinnity
// Description: Testbench for ALL_GATES

module ALL_GATES_sync_tb #(
    parameter WIDTH = 4
);

    logic clk;
    logic rst;
    logic [WIDTH-1:0] in1;
    logic [WIDTH-1:0] in2;

    logic [WIDTH-1:0] out_AND;
    logic [WIDTH-1:0] out_OR;
    logic [WIDTH-1:0] out_NOT;
    logic [WIDTH-1:0] out_NAND;
    logic [WIDTH-1:0] out_NOR;
    logic [WIDTH-1:0] out_XOR;
    logic [WIDTH-1:0] out_XNOR;

    // Device under test
    ALL_GATES_sync #(
        .WIDTH(WIDTH)
    ) dut (
        .clk(clk),
        .rst(rst),
        .in1(in1),
        .in2(in2),
        .out_AND(out_AND),
        .out_OR(out_OR),
        .out_NOT(out_NOT),
        .out_NAND(out_NAND),
        .out_NOR(out_NOR),
        .out_XOR(out_XOR),
        .out_XNOR(out_XNOR)
    );

    // 10 ns clock period
    initial clk = 1'b0;
    always #5 clk = ~clk;

    // Check expected outputs after the rising edge
    task automatic check_outputs;
        logic [WIDTH-1:0] exp_AND;
        logic [WIDTH-1:0] exp_OR;
        logic [WIDTH-1:0] exp_NOT;
        logic [WIDTH-1:0] exp_NAND;
        logic [WIDTH-1:0] exp_NOR;
        logic [WIDTH-1:0] exp_XOR;
        logic [WIDTH-1:0] exp_XNOR;
        begin
            if (rst) begin
                exp_AND  = '0;
                exp_OR   = '0;
                exp_NOT  = '0;
                exp_NAND = '0;
                exp_NOR  = '0;
                exp_XOR  = '0;
                exp_XNOR = '0;
            end else begin
                exp_AND  = in1 & in2;
                exp_OR   = in1 | in2;
                exp_NOT  = ~in1;
                exp_NAND = ~(in1 & in2);
                exp_NOR  = ~(in1 | in2);
                exp_XOR  = in1 ^ in2;
                exp_XNOR = ~(in1 ^ in2);
            end

            if (
                out_AND  !== exp_AND  ||
                out_OR   !== exp_OR   ||
                out_NOT  !== exp_NOT  ||
                out_NAND !== exp_NAND ||
                out_NOR  !== exp_NOR  ||
                out_XOR  !== exp_XOR  ||
                out_XNOR !== exp_XNOR
            ) begin
                $error("FAIL at time %0t: in1=%b in2=%b rst=%b",
                       $time, in1, in2, rst);
                $display("AND:  got %b expected %b", out_AND, exp_AND);
                $display("OR:   got %b expected %b", out_OR, exp_OR);
                $display("NOT:  got %b expected %b", out_NOT, exp_NOT);
                $display("NAND: got %b expected %b", out_NAND, exp_NAND);
                $display("NOR:  got %b expected %b", out_NOR, exp_NOR);
                $display("XOR:  got %b expected %b", out_XOR, exp_XOR);
                $display("XNOR: got %b expected %b", out_XNOR, exp_XNOR);
                $fatal(1, "Testbench failed.");
            end else begin
                $display("PASS at %0t: rst=%b in1=%b in2=%b",
                         $time, rst, in1, in2);
            end
        end
    endtask

    // Apply inputs away from the rising edge, then check after
    // sequential logic has updated.
    task automatic apply_and_check(
        input logic reset_value,
        input logic [WIDTH-1:0] a,
        input logic [WIDTH-1:0] b
    );
        begin
            @(negedge clk);
            rst = reset_value;
            in1 = a;
            in2 = b;

            @(posedge clk);
            #1;
            check_outputs();
        end
    endtask

    initial begin
        rst = 1'b1;
        in1 = '0;
        in2 = '0;

        // Reset test
        apply_and_check(1'b1, '0, '0);

        // Basic gate patterns
        apply_and_check(1'b0, '0, '0);
        apply_and_check(1'b0, '1, '0);
        apply_and_check(1'b0, '0, '1);
        apply_and_check(1'b0, '1, '1);

        // Mixed bit patterns
        apply_and_check(1'b0, {{(WIDTH-1){1'b0}}, 1'b1}, '1);
        apply_and_check(1'b0, '1, {{(WIDTH-1){1'b0}}, 1'b1});

        // Test that reset overrides nonzero inputs
        apply_and_check(1'b1, '1, '1);

        // Test normal operation after reset
        apply_and_check(1'b0, '1, '0);

        // Exhaustive testing for manageable widths
        if (WIDTH <= 8) begin
            for (int unsigned a = 0; a < (1 << WIDTH); a++) begin
                for (int unsigned b = 0; b < (1 << WIDTH); b++) begin
                    apply_and_check(
                        1'b0,
                        WIDTH'(a),
                        WIDTH'(b)
                    );
                end
            end
        end

        $display("ALL TESTS PASSED!");
        $finish;
    end

endmodule
