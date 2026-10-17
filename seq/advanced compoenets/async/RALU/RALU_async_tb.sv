
`timescale 1ns/1ps

module RALU_async_tb;

    parameter WIDTH = 4;

    logic clk;
    logic rst;
    logic [WIDTH-1:0] in1;
    logic [WIDTH-1:0] in2;
    logic [3:0] sel;
    logic [WIDTH-1:0] out1;

    integer passed = 0;
    integer failed = 0;

    RALU_async #(
        .WIDTH(WIDTH)
    ) DUT (
        .clk(clk),
        .rst(rst),
        .in1(in1),
        .in2(in2),
        .sel(sel),
        .out1(out1)
    );

    // 10 ns clock period
    always #5 clk = ~clk;

    task automatic check_output(
        input logic [3:0] opcode,
        input logic [WIDTH-1:0] expected,
        input string test_name
    );
        begin
            @(negedge clk);
            sel = opcode;

            @(posedge clk);
            #1;

            if (out1 === expected) begin
                $display("PASS: %-25s sel=%b out1=%b",
                         test_name, opcode, out1);
                passed++;
            end
            else begin
                $error("FAIL: %s | sel=%b | expected=%b | got=%b",
                       test_name, opcode, expected, out1);
                failed++;
            end
        end
    endtask

    initial begin
        clk = 0;
        rst = 0;
        in1 = 0;
        in2 = 0;
        sel = 4'b0011;

        // -------------------------
        // Asynchronous reset
        // -------------------------
        #2;
        rst = 1;
        #1;

        if (out1 === '0) begin
            $display("PASS: Asynchronous reset");
            passed++;
        end
        else begin
            $error("FAIL: Asynchronous reset | got=%b", out1);
            failed++;
        end

        @(negedge clk);
        rst = 0;

        // Load in1_r = 5, in2_r = 3
        in1 = 4'b0101;
        in2 = 4'b0011;
        check_output(4'b1111, 4'b0000, "Load inputs");

        // Logic operations
        check_output(4'b0000, 4'b0001, "AND: 5 & 3");
        check_output(4'b0001, 4'b0111, "OR: 5 | 3");
        check_output(4'b0010, 4'b1010, "NOT: ~5");
        check_output(4'b0011, 4'b1010, "Hold");

        // Arithmetic operations
        check_output(4'b0100, 4'b1000, "Add: 5 + 3");
        check_output(4'b0101, 4'b0110, "XOR: 5 ^ 3");
        check_output(4'b0110, 4'b0010, "Subtract: 5 - 3");

        // Shifts
        check_output(4'b0111, 4'b1010, "Left shift: 5");
        check_output(4'b1000, 4'b0010, "Right shift: 5");

        // Two's complement
        check_output(4'b1001, 4'b1011, "Two's complement: -5");

        // Increment and decrement
        check_output(4'b1100, 4'b0110, "Increment: 5 + 1");
        check_output(4'b1101, 4'b0100, "Decrement: 5 - 1");

        // Wire in1_r to output
        check_output(4'b1110, 4'b0101, "Wire in1");

        // Load in2_r into in1_r; output holds previous value
        check_output(4'b1010, 4'b0101, "Load in2 into in1");

        // Verify in1_r now contains 3
        check_output(4'b1110, 4'b0011, "Verify in2 loaded");

        // Load current out1_r (3) into in1_r
        check_output(4'b1011, 4'b0011, "Feedback output to in1");

        // Verify feedback value
        check_output(4'b1110, 4'b0011, "Verify feedback");

        // Hold should preserve output when external inputs change
        @(negedge clk);
        in1 = 4'b1111;
        in2 = 4'b0000;
        sel = 4'b0011;

        @(posedge clk);
        #1;

        if (out1 === 4'b0011) begin
            $display("PASS: Hold ignores external input changes");
            passed++;
        end
        else begin
            $error("FAIL: Hold | expected=0011 | got=%b", out1);
            failed++;
        end

        // Summary
        $display("");
        $display("==============================");
        $display("Tests passed: %0d", passed);
        $display("Tests failed: %0d", failed);
        $display("==============================");

        if (failed == 0)
            $display("ALL TESTS PASSED!");
        else
            $fatal(1, "Some tests failed.");

        $finish;
    end

endmodule
