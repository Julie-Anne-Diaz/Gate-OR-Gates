//Abhiram Pinnity
// Description: TB to test Structurally combined module for gate logic

module ALL_GATES_tb #(
    parameter WIDTH = 4
);
    logic [WIDTH-1:0] in1;
    logic [WIDTH-1:0] in2;
    logic [WIDTH-1:0] out_AND;
    logic [WIDTH-1:0] out_OR;
    logic [WIDTH-1:0] out_NOT;
    logic [WIDTH-1:0] out_NAND;
    logic [WIDTH-1:0] out_NOR;
    logic [WIDTH-1:0] out_XOR;
    logic [WIDTH-1:0] out_XNOR;
    integer errors = 0;

    ALL_GATES dut (
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

    initial begin
        in1 = 4'b0000;
        in2 = 4'b0000;

        // Load 0000 in both inputs and see if it works
        #1;
        in1 = 4'b0000;
        in2 = 4'b0000;

        #1;
        assert (out_AND === (in1 & in2))
            else begin
                $error("AND: expected output 0000");
                errors++;
            end
        assert (out_OR === (in1 | in2))
            else begin
                $error("OR: expected output 0000");
                errors++;
            end
        assert (out_NOT === ~in1)
            else begin
                $error("NOT: expected output 1111");
                errors++;
            end
        assert (out_NAND === ~(in1 & in2))
            else begin
                $error("NAND: expected output 1111");
                errors++;
            end
        assert (out_NOR === ~(in1 | in2))
            else begin
                $error("NOR: expected output 1111");
                errors++;
            end
        assert (out_XOR === (in1 ^ in2))
            else begin
                $error("XOR: expected output 0000");
                errors++;
            end
        assert (out_XNOR === ~(in1 ^ in2))
            else begin
                $error("XNOR: expected output 1111");
                errors++;
            end

        // Load 0001 for in1 and see if it works
        #1;
        in1 = 4'b0001;
        in2 = 4'b0000;

        #1;
        assert (out_AND === (in1 & in2))
            else begin
                $error("AND: expected output 0000");
                errors++;
            end
        assert (out_OR === (in1 | in2))
            else begin
                $error("OR: expected output 0001");
                errors++;
            end
        assert (out_NOT === ~in1)
            else begin
                $error("NOT: expected output 1110");
                errors++;
            end
        assert (out_NAND === ~(in1 & in2))
            else begin
                $error("NAND: expected output 1111");
                errors++;
            end
        assert (out_NOR === ~(in1 | in2))
            else begin
                $error("NOR: expected output 1110");
                errors++;
            end
        assert (out_XOR === (in1 ^ in2))
            else begin
                $error("XOR: expected output 0001");
                errors++;
            end
        assert (out_XNOR === ~(in1 ^ in2))
            else begin
                $error("XNOR: expected output 1110");
                errors++;
            end

        // Load 0001 for in2 and see if it works
        #1;
        in1 = 4'b0000;
        in2 = 4'b0001;

        #1;
        assert (out_AND === (in1 & in2))
            else begin
                $error("AND: expected output 0000");
                errors++;
            end
        assert (out_OR === (in1 | in2))
            else begin
                $error("OR: expected output 0001");
                errors++;
            end
        assert (out_NOT === ~in1)
            else begin
                $error("NOT: expected output 1111");
                errors++;
            end
        assert (out_NAND === ~(in1 & in2))
            else begin
                $error("NAND: expected output 1111");
                errors++;
            end
        assert (out_NOR === ~(in1 | in2))
            else begin
                $error("NOR: expected output 1110");
                errors++;
            end
        assert (out_XOR === (in1 ^ in2))
            else begin
                $error("XOR: expected output 0001");
                errors++;
            end
        assert (out_XNOR === ~(in1 ^ in2))
            else begin
                $error("XNOR: expected output 1110");
                errors++;
            end

        // Load 0001 in both inputs and see if it works
        #1;
        in1 = 4'b0001;
        in2 = 4'b0001;

        #1;
        assert (out_AND === (in1 & in2))
            else begin
                $error("AND: expected output 0001");
                errors++;
            end
        assert (out_OR === (in1 | in2))
            else begin
                $error("OR: expected output 0001");
                errors++;
            end
        assert (out_NOT === ~in1)
            else begin
                $error("NOT: expected output 1110");
                errors++;
            end
        assert (out_NAND === ~(in1 & in2))
            else begin
                $error("NAND: expected output 1110");
                errors++;
            end
        assert (out_NOR === ~(in1 | in2))
            else begin
                $error("NOR: expected output 1110");
                errors++;
            end
        assert (out_XOR === (in1 ^ in2))
            else begin
                $error("XOR: expected output 0000");
                errors++;
            end
        assert (out_XNOR === ~(in1 ^ in2))
            else begin
                $error("XNOR: expected output 1111");
                errors++;
            end

        // Load 1001 in1 and 1111 in2 and see if it works
        #1;
        in1 = 4'b1001;
        in2 = 4'b1111;

        #1;
        assert (out_AND === (in1 & in2))
            else begin
                $error("AND: expected output 1001");
                errors++;
            end
        assert (out_OR === (in1 | in2))
            else begin
                $error("OR: expected output 1111");
                errors++;
            end
        assert (out_NOT === ~in1)
            else begin
                $error("NOT: expected output 0110");
                errors++;
            end
        assert (out_NAND === ~(in1 & in2))
            else begin
                $error("NAND: expected output 0110");
                errors++;
            end
        assert (out_NOR === ~(in1 | in2))
            else begin
                $error("NOR: expected output 0000");
                errors++;
            end
        assert (out_XOR === (in1 ^ in2))
            else begin
                $error("XOR: expected output 0110");
                errors++;
            end
        assert (out_XNOR === ~(in1 ^ in2))
            else begin
                $error("XNOR: expected output 1001");
                errors++;
            end

        #1;

        // Print final test result
        if (errors == 0)
            $display("ALL TESTS PASSED!");
        else
            $display("TESTS FAILED! Total failures: %0d", errors);

        $finish;
    end

    // Safety timeout
    initial begin
        #1000;
        $fatal(1, "Testbench timeout");
    end

endmodule