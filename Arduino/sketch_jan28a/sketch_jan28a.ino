#include "HX711.h"
HX711 scale;
float calibration_factor = -52000;
void setup() {
Serial.begin(9600);
scale.begin(2,3); //dt 2 sck3
scale.set_scale();
scale.tare(); //Reset the scale to 0
}
void loop() {
scale.set_scale(calibration_factor);
Serial.print(scale.get_units());
Serial.println(" kg");
delay(500);
}
//[출처] 아두이노 3선 로드셀 1개 사용하기(hx711)|작성자 브로콜리소년
