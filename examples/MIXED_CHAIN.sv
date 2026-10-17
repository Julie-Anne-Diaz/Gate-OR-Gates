// Five independent scalar inputs, one output, and mixed gate sizes.
// No bus replication: y = ((a XOR b) AND (c OR d)) XOR (NOT e).
// Yosys may merge the final XOR + NOT into an XNOR.
module MIXED_CHAIN (
    input wire a, b, c, d, e,
    output wire y
);
    wire parity = a ^ b;
    wire enabled = c | d;
    wire masked = parity & enabled;
    assign y = masked ^ (~e);
endmodule
