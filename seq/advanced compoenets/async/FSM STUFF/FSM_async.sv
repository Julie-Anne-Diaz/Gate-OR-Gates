
module FSM_async(
    input  logic clk,
    input  logic rst,
    input  logic in,
    output logic alarm_on,
    output logic lock,
    output logic unlock
);

    logic [1:0] wrong_attempts, wrong_attempts_next;
    logic [2:0] code = 3'b101;

    typedef enum logic [2:0] {
        START,
        ONE_RIGHT,
        TWO_RIGHT,
        UNLOCK,
        ALARM
    } state_t;

    state_t c_state, n_state;

    // State and counter registers
    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            c_state        <= START;
            wrong_attempts <= 2'b00;
        end
        else begin
            c_state        <= n_state;
            wrong_attempts <= wrong_attempts_next;
        end
    end

    // Next-state logic and outputs
    always_comb begin
        n_state = c_state;
        wrong_attempts_next = wrong_attempts;

        lock     = 1'b1;
        unlock   = 1'b0;
        alarm_on = 1'b0;

        case (c_state)
            START: begin
                if (in == code[0])
                    n_state = ONE_RIGHT;
                else if (wrong_attempts == 2'b10) begin
                    n_state = ALARM;
                    wrong_attempts_next = 2'b00;
                end
                else begin
                    wrong_attempts_next = wrong_attempts + 1'b1;
                    n_state = START;
                end
            end

            ONE_RIGHT: begin
                if (in == code[1])
                    n_state = TWO_RIGHT;
                else if (wrong_attempts == 2'b10) begin
                    n_state = ALARM;
                    wrong_attempts_next = 2'b00;
                end
                else begin
                    wrong_attempts_next = wrong_attempts + 1'b1;
                    n_state = START;
                end
            end

            TWO_RIGHT: begin
                if (in == code[2])
                    n_state = UNLOCK;
                else if (wrong_attempts == 2'b10) begin
                    n_state = ALARM;
                    wrong_attempts_next = 2'b00;
                end
                else begin
                    wrong_attempts_next = wrong_attempts + 1'b1;
                    n_state = START;
                end
            end

            UNLOCK: begin
                lock    = 1'b0;
                unlock  = 1'b1;
                n_state = UNLOCK;
            end

            ALARM: begin
                alarm_on = 1'b1;
                n_state  = ALARM;
            end

            default: begin
                n_state = START;
                wrong_attempts_next = 2'b00;
            end
        endcase
    end

endmodule
