
`timescale 1ns/1ps

module shift_reg_async_tb;

    logic clk;
    logic rst;
    logic in1;
    logic out1;

    integer passed = 0;
    integer failed = 0;

    // Device under test
    shift_reg_async DUT (
        .clk(clk),
        .rst(rst),
        .in1(in1),
        .out1(out1)
    );

    // 10 ns clock period
    always #5 clk = ~clk;

    // Check output against expected value
    task automatic check_output(
        input logic expected,
        input string test_name
    );
        begin
            #1;

            if (out1 === expected) begin
                $display("PASS: %s | out1=%b", test_name, out1);
                passed++;
            end
            else begin
                $error("FAIL: %s | expected=%b | got=%b",
                       test_name, expected, out1);
                failed++;
            end
        end
    endtask

    initial begin
        clk = 0;
        rst = 0;
        in1 = 0;

        // -------------------------
        // Test 1: Asynchronous reset
        // -------------------------
        #2;
        rst = 1;
        check_output(0, "Asynchronous reset");

        @(negedge clk);
        rst = 0;

        // -------------------------
        // Test 2: Shift a single 1
        // -------------------------
        in1 = 1;

        @(posedge clk);
        check_output(0, "1st clock: output still 0");

        @(negedge clk);
        in1 = 0;

        @(posedge clk);
        check_output(0, "2nd clock: output still 0");

        @(posedge clk);
        check_output(0, "3rd clock: output still 0");

        @(posedge clk);
        check_output(1, "4th clock: output becomes 1");

        // -------------------------
        // Test 3: Shift the 1 out
        // -------------------------
        @(posedge clk);
        check_output(0, "5th clock: output returns to 0");

        // -------------------------
        // Test 4: Reset while running
        // -------------------------
        @(negedge clk);
        in1 = 1;

        @(posedge clk);
        #1;

        // Assert reset between clock edges
        #1;
        rst = 1;
        check_output(0, "Reset clears output immediately");

        @(negedge clk);
        rst = 0;
        in1 = 0;

        // -------------------------
        // Summary
        // -------------------------
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
