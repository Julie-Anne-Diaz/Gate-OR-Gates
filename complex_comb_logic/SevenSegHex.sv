module SevenSegHex (
    input  logic A, B, C, D,
    output logic seg_a, seg_b, seg_c,
                 seg_d, seg_e, seg_f, seg_g
);

    always_comb begin
        case ({A, B, C, D})
            4'b0000: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b1000000;
            4'b0001: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b1111001;
            4'b0010: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0100100;
            4'b0011: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0110000;
            4'b0100: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0011001;
            4'b0101: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0010010;
            4'b0110: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0000010;
            4'b0111: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b1111000;
            4'b1000: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0000000;
            4'b1001: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0010000;
            4'b1010: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0001000;
            4'b1011: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0000011;
            4'b1100: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b1000110;
            4'b1101: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0100001;
            4'b1110: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0000110;
            4'b1111: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b0001110;
            default: {seg_a,seg_b,seg_c,seg_d,seg_e,seg_f,seg_g} = 7'b1111111;
        endcase
    end

endmodule