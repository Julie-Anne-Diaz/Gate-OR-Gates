
module FSM_STOPWATCH(
    input  logic clk,
    input  logic rst,
    input  logic go,
    input logic pause,
    input logic lap,
    input logic stop,

    output logic run_en,
    output logic lap_en,
    output logic stop_sel
);

    typedef enum logic [2:0] {
        IDLE,
        RUNNING,
        PAUSED,
        LAP_STORE,
        STOPPED
    } state_t;

    state_t c_state, n_state;

    logic go_q;
    logic go_rise;

    // State and counter registers
    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            c_state        <= IDLE;
        end
        else begin
            c_state        <= n_state;
        end
    end

    always_ff @(posedge clk)
        go_q <= go;

    assign go_rise = go & ~go_q;

    // Next-state logic and outputs
    always_comb begin
        n_state = c_state;
        run_en = 1'b0;
        lap_en = 1'b0;
        stop_sel = 1'b0;


        case (c_state)
            IDLE: begin
                if (go_rise) n_state = RUNNING;
            end

            RUNNING: begin
                run_en = 1'b1;
                if (lap) begin
                    n_state = LAP_STORE;
                    lap_en = 1'b1;
                end
                else if (pause) begin
                    n_state = PAUSED;
                end
            end

            PAUSED: begin
                if (stop) begin
                    n_state = STOPPED;
                end
                else if (~pause) n_state = RUNNING;
            end

            LAP_STORE: begin
                run_en = 1'b1;
                if(pause) n_state = PAUSED;
                else if(~lap) n_state = RUNNING;
            end

            STOPPED: begin
                stop_sel = 1'b1;
                n_state  = IDLE;
            end

            default: begin
                n_state = IDLE;
            end
        endcase
    end

endmodule