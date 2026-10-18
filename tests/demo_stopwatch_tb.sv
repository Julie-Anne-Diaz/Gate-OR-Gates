module demo_stopwatch_tb;
    reg clk=0, rst=1, go=0, pause=0, lap=0, stop=0, show_lap=0;
    wire [3:0] h0,h1,h2,h3;
    wire [7:0] r0,r1,r2,r3,r4,r5;
    MINECRAFT_TOP dut(.*,.HEX0(h0),.HEX1(h1),.HEX2(h2),.HEX3(h3));
    TOP_LVL reference (
        .MAX10_CLK1_50(clk),.KEY({1'b1,~rst}),
        .SW({show_lap,5'b0,stop,lap,pause,go}),
        .HEX0(r0),.HEX1(r1),.HEX2(r2),.HEX3(r3),.HEX4(r4),.HEX5(r5)
    );
    integer cycles=0, value, rng=7364;
    reg [15:0] saved;
    task cycle;
        begin
            #2; clk=1; #2;
            cycles=cycles+1;
            if (dut.count !== reference.count || dut.lap_count !== reference.lap_count)
                $fatal(1,"Storage differs at cycle %0d",cycles);
            if ({h3,h2,h1,h0} !== {reference.d3,reference.d2,reference.d1,reference.d0})
                $fatal(1,"Digits differ at cycle %0d",cycles);
            clk=0; #2;
        end
    endtask
    wire [3:0] b0,b1,b2,b3;
    BINARY14_TO_BCD converter(.value(value[13:0]),.digits({b3,b2,b1,b0}));
    initial begin
        // The Minecraft adaptation intentionally advances on every clock.
        force reference.tick = 1'b1;
        for (value=0; value<16384; value=value+1) begin
            #1;
            if (b0 !== value%10 || b1 !== (value/10)%10 ||
                b2 !== (value/100)%10 || b3 !== (value/1000)%10)
                $fatal(1,"BCD mismatch at %0d",value);
        end
        repeat(4) cycle(); rst=0; repeat(4) cycle();
        go=1; repeat(5) cycle();
        if (!dut.run_en) $fatal(1,"Did not start");
        repeat(10020) cycle(); // Includes 9999 -> 0000 rollover.
        lap=1; repeat(6) cycle(); saved=dut.lap_count;
        repeat(6) cycle();
        if (dut.lap_count !== saved || dut.count == saved) $fatal(1,"Lap did not hold");
        show_lap=1; repeat(4) cycle();
        pause=1; repeat(6) cycle(); saved=dut.count;
        repeat(6) cycle();
        if (dut.count !== saved) $fatal(1,"Pause did not hold");
        stop=1; repeat(6) cycle();
        if (dut.count !== 0 || dut.lap_count !== 0) $fatal(1,"Stop did not clear");
        go=0;pause=0;stop=0;lap=0;show_lap=0;repeat(5) cycle();
        go=1;repeat(5) cycle();
        for (integer i=0;i<1000;i=i+1) begin
            {go,pause,lap,stop,show_lap}=$random(rng);
            cycle();
        end
        // Reset while the clock is low must clear storage asynchronously.
        rst=1; #1;
        if (dut.count !== 0 || dut.lap_count !== 0) $fatal(1,"Async reset failed");
        repeat(4) cycle();
        $display("PASS: all 16384 BCD values, %0d reference cycles, rollover/lap/pause/stop/reset",cycles);
        $finish;
    end
endmodule
