int period = 2; //period of duty cycle in seconds
float on_frac = 0; //default duty cycle
long last_read = 0;


void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT);
}


float get_temp() {
  float voltage;
  voltage = analogRead(A0) * 5.0 / 1024;
  return (voltage - 1.25) / 0.005;
}

void loop() {
  
  if (Serial.available())
  {
    String cmd;
    last_read = millis();
    on_frac = Serial.readStringUntil('\n').toFloat();
  }


  // reset on frac after a period of no serial reads.
  // this is to prevent overheating
  if ((millis() - last_read) > 10000) {
    on_frac = 0;
  }
  dutyCycle(on_frac);

  float sum = 0;
  int num_pts = 15;
  int tdelay = 1;

  for (int i = 0; i < num_pts; i++) {
    sum += get_temp();
    delay(tdelay);
  }

  Serial.print(String(millis()) + ", ");
  Serial.println( sum / num_pts );
}

void dutyCycle(float on_frac) {
  if (on_frac > 0) {
    digitalWrite(13, HIGH);
    delay(1000 * period * on_frac);
  }
  digitalWrite(13, LOW);
  delay(1000 * period * (1 - on_frac));
}
