// FPGA GPIO -> UNO INPUT only. Preserve common GND. No INPUT_PULLUP.
const byte switchPins[10] = {2,3,4,5,6,7,8,9,10,11};
const byte keyPins[2] = {12,A0};
const unsigned long debounceMs = 15;
bool rawKeys[2], stableKeys[2];
unsigned long changedAt[2] = {0,0};
uint32_t presses[2] = {0,0};
int previousSwitches = -1;
unsigned long lastSend = 0;

void setup() {
  Serial.begin(115200);
  for (byte i=0; i<10; i++) pinMode(switchPins[i], INPUT);
  for (byte i=0; i<2; i++) {
    pinMode(keyPins[i], INPUT);
    rawKeys[i] = stableKeys[i] = digitalRead(keyPins[i]) == HIGH;
    changedAt[i] = millis();
  }
}
void loop() {
  const unsigned long now = millis();
  int switches = 0;
  for (byte i=0; i<10; i++) switches |= digitalRead(switchPins[i]) << i;
  bool event = false;
  for (byte i=0; i<2; i++) {
    bool raw = digitalRead(keyPins[i]) == HIGH;
    if (raw != rawKeys[i]) { rawKeys[i] = raw; changedAt[i] = now; }
    if (raw != stableKeys[i] && (unsigned long)(now - changedAt[i]) >= debounceMs) {
      stableKeys[i] = raw;
      if (raw) { presses[i]++; event = true; }
    }
  }
  if (switches != previousSwitches || event || (unsigned long)(now-lastSend) >= 500) {
    // Versioned protocol: switch HEX, then decimal monotonic button counters.
    Serial.print("V2 "); Serial.print(switches, HEX);
    Serial.print(' '); Serial.print(presses[0]);
    Serial.print(' '); Serial.println(presses[1]);
    previousSwitches = switches; lastSend = now;
  }
  delay(1);
}
