// Abhiram Pinnity
// Description: Testbench for structural 8 to 1 mux

module mux_tb #(
    parameter WIDTH = 4
);

    logic [WIDTH-1:0] in1, in2, in3, in4;
    logic [WIDTH-1:0] in5, in6, in7, in8;
    logic [2:0] sel;
    logic [WIDTH-1:0] out1;

    integer errors = 0;

    // Instantiate the DUT
    mux_8 #(.WIDTH(WIDTH)) dut (
        .in1(in1),
        .in2(in2),
        .in3(in3),
        .in4(in4),
        .in5(in5),
        .in6(in6),
        .in7(in7),
        .in8(in8),
        .sel(sel),
        .out1(out1)
    );

    initial begin

        // Test 1: Select in1
        in1 = 4'b0001;
        in2 = 4'b0010;
        in3 = 4'b0011;
        in4 = 4'b0100;
        in5 = 4'b0101;
        in6 = 4'b0110;
        in7 = 4'b0111;
        in8 = 4'b1000;
        sel = 3'b000;
        #1;
        assert (out1 == in1)
        else begin
            $error("Test 1 failed: sel=000, expected in1");
            errors++;
        end

        // Test 2: Select in2
        sel = 3'b001;
        #1;
        assert (out1 == in2)
        else begin
            $error("Test 2 failed: sel=001, expected in2");
            errors++;
        end

        // Test 3: Select in3
        sel = 3'b010;
        #1;
        assert (out1 == in3)
        else begin
            $error("Test 3 failed: sel=010, expected in3");
            errors++;
        end

        // Test 4: Select in4
        sel = 3'b011;
        #1;
        assert (out1 == in4)
        else begin
            $error("Test 4 failed: sel=011, expected in4");
            errors++;
        end

        // Test 5: Select in5
        sel = 3'b100;
        #1;
        assert (out1 == in5)
        else begin
            $error("Test 5 failed: sel=100, expected in5");
            errors++;
        end

        // Test 6: Select in6
        sel = 3'b101;
        #1;
        assert (out1 == in6)
        else begin
            $error("Test 6 failed: sel=101, expected in6");
            errors++;
        end

        // Test 7: Select in7
        sel = 3'b110;
        #1;
        assert (out1 == in7)
        else begin
            $error("Test 7 failed: sel=110, expected in7");
            errors++;
        end

        // Test 8: Select in8
        sel = 3'b111;
        #1;
        assert (out1 == in8)
        else begin
            $error("Test 8 failed: sel=111, expected in8");
            errors++;
        end

        // Final result
        if (errors == 0)
            $display("ALL TESTS PASSED!");
        else
            $display("TESTS FAILED! Total failures: %0d", errors);

        $finish;
    end

    // Timeout protection
    initial begin
        #100;
        $fatal(1, "Testbench timeout");
    end

endmodule
