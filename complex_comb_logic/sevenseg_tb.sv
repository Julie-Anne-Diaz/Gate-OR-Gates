// Name: Abhiram Pinnity
// Description: Testbench for 7-segment display decoder

module sevenseg_tb;

    logic [3:0] bin_in;
    logic [6:0] seg_out;

    integer errors = 0;
    integer tests = 0;

    // Instantiate the DUT
    sevenseg dut (
        .bin_in(bin_in),
        .seg_out(seg_out)
    );

    initial begin

        // Test 0
        bin_in = 4'b0000;
        #1;
        tests++;
        assert (seg_out === 7'b1000000)
        else begin
            $error("Test 0 failed: got %b, expected 1000000", seg_out);
            errors++;
        end

        // Test 1
        bin_in = 4'b0001;
        #1;
        tests++;
        assert (seg_out === 7'b1111001)
        else begin
            $error("Test 1 failed: got %b, expected 1111001", seg_out);
            errors++;
        end

        // Test 2
        bin_in = 4'b0010;
        #1;
        tests++;
        assert (seg_out === 7'b0100100)
        else begin
            $error("Test 2 failed: got %b, expected 0100100", seg_out);
            errors++;
        end

        // Test 3
        bin_in = 4'b0011;
        #1;
        tests++;
        assert (seg_out === 7'b0110000)
        else begin
            $error("Test 3 failed: got %b, expected 0110000", seg_out);
            errors++;
        end

        // Test 4
        bin_in = 4'b0100;
        #1;
        tests++;
        assert (seg_out === 7'b0011001)
        else begin
            $error("Test 4 failed: got %b, expected 0011001", seg_out);
            errors++;
        end

        // Test 5
        bin_in = 4'b0101;
        #1;
        tests++;
        assert (seg_out === 7'b0010010)
        else begin
            $error("Test 5 failed: got %b, expected 0010010", seg_out);
            errors++;
        end

        // Test 6
        bin_in = 4'b0110;
        #1;
        tests++;
        assert (seg_out === 7'b0000010)
        else begin
            $error("Test 6 failed: got %b, expected 0000010", seg_out);
            errors++;
        end

        // Test 7
        bin_in = 4'b0111;
        #1;
        tests++;
        assert (seg_out === 7'b1111000)
        else begin
            $error("Test 7 failed: got %b, expected 1111000", seg_out);
            errors++;
        end

        // Test 8
        bin_in = 4'b1000;
        #1;
        tests++;
        assert (seg_out === 7'b0000000)
        else begin
            $error("Test 8 failed: got %b, expected 0000000", seg_out);
            errors++;
        end

        // Test 9
        bin_in = 4'b1001;
        #1;
        tests++;
        assert (seg_out === 7'b0010000)
        else begin
            $error("Test 9 failed: got %b, expected 0010000", seg_out);
            errors++;
        end

        // Test A
        bin_in = 4'b1010;
        #1;
        tests++;
        assert (seg_out === 7'b0001000)
        else begin
            $error("Test A failed: got %b, expected 0001000", seg_out);
            errors++;
        end

        // Test B
        bin_in = 4'b1011;
        #1;
        tests++;
        assert (seg_out === 7'b0000011)
        else begin
            $error("Test B failed: got %b, expected 0000011", seg_out);
            errors++;
        end

        // Test C
        bin_in = 4'b1100;
        #1;
        tests++;
        assert (seg_out === 7'b1000110)
        else begin
            $error("Test C failed: got %b, expected 1000110", seg_out);
            errors++;
        end

        // Test D
        bin_in = 4'b1101;
        #1;
        tests++;
        assert (seg_out === 7'b0100001)
        else begin
            $error("Test D failed: got %b, expected 0100001", seg_out);
            errors++;
        end

        // Test E
        bin_in = 4'b1110;
        #1;
        tests++;
        assert (seg_out === 7'b0000110)
        else begin
            $error("Test E failed: got %b, expected 0000110", seg_out);
            errors++;
        end

        // Test F
        bin_in = 4'b1111;
        #1;
        tests++;
        assert (seg_out === 7'b0001110)
        else begin
            $error("Test F failed: got %b, expected 0001110", seg_out);
            errors++;
        end

        // Final report
        $display("--------------------------------");
        $display("Tests run: %0d", tests);
        $display("Errors:    %0d", errors);

        if (errors == 0)
            $display("ALL TESTS PASSED!");
        else
            $display("SOME TESTS FAILED!");

        $display("--------------------------------");
        $finish;
    end

    // Timeout protection
    initial begin
        #100;
        $fatal(1, "Testbench timeout!");
    end

endmodule