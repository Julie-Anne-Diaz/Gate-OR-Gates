// Abhiram Pinnity
// Description: Testbench for 4-bit ALU

module ALU_4bit_tb;

    logic [3:0] in1;
    logic [3:0] in2;
    logic [3:0] sel;
    logic [3:0] out1;

    integer errors = 0;
    integer tests = 0;

    // Instantiate the DUT
    ALU_4bit #(.WIDTH(4)) dut (
        .in1(in1),
        .in2(in2),
        .sel(sel),
        .out1(out1)
    );

    initial begin
        // Test inputs
        in1 = 4'b1010;
        in2 = 4'b1100;

        // 0000: AND
        sel = 4'b0000;
        #1;
        tests++;
        assert (out1 === 4'b1000)
        else begin
            $error("AND failed: got %b, expected 1000", out1);
            errors++;
        end

        // 0001: OR
        sel = 4'b0001;
        #1;
        tests++;
        assert (out1 === 4'b1110)
        else begin
            $error("OR failed: got %b, expected 1110", out1);
            errors++;
        end

        // 0010: NOT in1
        sel = 4'b0010;
        #1;
        tests++;
        assert (out1 === 4'b0101)
        else begin
            $error("NOT failed: got %b, expected 0101", out1);
            errors++;
        end

        // 0011: NOR
        sel = 4'b0011;
        #1;
        tests++;
        assert (out1 === 4'b0001)
        else begin
            $error("NOR failed: got %b, expected 0001", out1);
            errors++;
        end

        // 0100: NAND
        sel = 4'b0100;
        #1;
        tests++;
        assert (out1 === 4'b0111)
        else begin
            $error("NAND failed: got %b, expected 0111", out1);
            errors++;
        end

        // 0101: XOR
        sel = 4'b0101;
        #1;
        tests++;
        assert (out1 === 4'b0110)
        else begin
            $error("XOR failed: got %b, expected 0110", out1);
            errors++;
        end

        // 0110: XNOR
        sel = 4'b0110;
        #1;
        tests++;
        assert (out1 === 4'b1001)
        else begin
            $error("XNOR failed: got %b, expected 1001", out1);
            errors++;
        end

        // 0111: Left shift in1
        sel = 4'b0111;
        #1;
        tests++;
        assert (out1 === 4'b0100)
        else begin
            $error("Left shift failed: got %b, expected 0100", out1);
            errors++;
        end

        // 1000: Right shift in1
        sel = 4'b1000;
        #1;
        tests++;
        assert (out1 === 4'b0101)
        else begin
            $error("Right shift failed: got %b, expected 0101", out1);
            errors++;
        end

        // 1001: Two's-complement negation of in1
        sel = 4'b1001;
        #1;
        tests++;
        assert (out1 === 4'b0110)
        else begin
            $error("Negation failed: got %b, expected 0110", out1);
            errors++;
        end

        // 1010: Reverse bits of in1
        sel = 4'b1010;
        #1;
        tests++;
        assert (out1 === 4'b0101)
        else begin
            $error("Reverse in1 failed: got %b, expected 0101", out1);
            errors++;
        end

        // 1011: Reverse bits of in2
        sel = 4'b1011;
        #1;
        tests++;
        assert (out1 === 4'b0011)
        else begin
            $error("Reverse in2 failed: got %b, expected 0011", out1);
            errors++;
        end

        // 1100: Increment in1
        sel = 4'b1100;
        #1;
        tests++;
        assert (out1 === 4'b1011)
        else begin
            $error("Increment failed: got %b, expected 1011", out1);
            errors++;
        end

        // 1101: Decrement in1
        sel = 4'b1101;
        #1;
        tests++;
        assert (out1 === 4'b1001)
        else begin
            $error("Decrement failed: got %b, expected 1001", out1);
            errors++;
        end

        // 1110: Pass through in1
        sel = 4'b1110;
        #1;
        tests++;
        assert (out1 === in1)
        else begin
            $error("Pass in1 failed: got %b, expected %b", out1, in1);
            errors++;
        end

        // 1111: Pass through in2
        sel = 4'b1111;
        #1;
        tests++;
        assert (out1 === in2)
        else begin
            $error("Pass in2 failed: got %b, expected %b", out1, in2);
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
