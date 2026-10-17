`timescale 1ns/1ps

module FSM_async_tb;

    logic clk;
    logic rst;
    logic in;
    logic alarm_on;
    logic lock;
    logic unlock;

    integer passed = 0;
    integer failed = 0;

    // Device under test
    FSM_async DUT (
        .clk(clk),
        .rst(rst),
        .in(in),
        .alarm_on(alarm_on),
        .lock(lock),
        .unlock(unlock)
    );

    // 10 ns clock period
    always #5 clk = ~clk;

    // Apply input on falling edge, check outputs after rising edge
    task automatic apply_bit(
        input logic bit_value,
        input logic expected_lock,
        input logic expected_unlock,
        input logic expected_alarm,
        input string test_name
    );
        begin
            @(negedge clk);
            in = bit_value;

            @(posedge clk);
            #1;

            // Debug output
            $display(
                "DEBUG: %s | input=%b state=%0d wrong_attempts=%0d alarm=%b",
                test_name, in, DUT.c_state,
                DUT.wrong_attempts, alarm_on
            );

            if (lock === expected_lock &&
                unlock === expected_unlock &&
                alarm_on === expected_alarm) begin
                $display(
                    "PASS: %s | lock=%b unlock=%b alarm=%b",
                    test_name, lock, unlock, alarm_on
                );
                passed++;
            end
            else begin
                $error(
                    "FAIL: %s | expected lock=%b unlock=%b alarm=%b | got lock=%b unlock=%b alarm=%b",
                    test_name,
                    expected_lock, expected_unlock, expected_alarm,
                    lock, unlock, alarm_on
                );
                failed++;
            end
        end
    endtask

    // Apply asynchronous reset.
    // Reset is asserted at a falling edge, checked immediately (async),
    // held through one rising edge, then released just after that edge.
    // The next apply_bit therefore starts from a clean START state with
    // no stray clock edge in between.
    task automatic reset_dut;
        begin
            @(negedge clk);
            rst = 1'b1;
            #1;

            if (lock === 1'b1 &&
                unlock === 1'b0 &&
                alarm_on === 1'b0) begin
                $display("PASS: Reset");
                passed++;
            end
            else begin
                $error(
                    "FAIL: Reset | lock=%b unlock=%b alarm=%b",
                    lock, unlock, alarm_on
                );
                failed++;
            end

            @(posedge clk);   // hold reset through a clock edge
            #1;
            rst = 1'b0;       // release; next edge belongs to apply_bit
        end
    endtask

    initial begin
        clk = 1'b0;
        rst = 1'b0;
        in  = 1'b0;

        // Initialize the FSM
        reset_dut();

        // Test 1: Correct code 101
        apply_bit(1, 1, 0, 0, "Correct code bit 1");
        apply_bit(0, 1, 0, 0, "Correct code bit 2");
        apply_bit(1, 0, 1, 0, "Correct code unlocks");

        // Unlock should persist
        apply_bit(0, 0, 1, 0, "Unlock remains active");

        reset_dut();

        // Test 2: Incorrect bit then correct code
        apply_bit(0, 1, 0, 0, "First incorrect bit");
        apply_bit(1, 1, 0, 0, "Next bit matches first code bit");
        apply_bit(0, 1, 0, 0, "Next bit matches second code bit");
        apply_bit(1, 0, 1, 0, "Unlock after correct sequence");

        reset_dut();

        // Test 3: Three incorrect bits
        apply_bit(0, 1, 0, 0, "Incorrect bit 1");
        apply_bit(0, 1, 0, 0, "Incorrect bit 2");
        apply_bit(0, 1, 0, 1, "Incorrect bit 3 triggers alarm");

        // Alarm should persist until reset
        apply_bit(1, 1, 0, 1, "Alarm remains active");

        reset_dut();

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