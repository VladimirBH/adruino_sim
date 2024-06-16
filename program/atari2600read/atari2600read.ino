#define BUTTON_UP 3
#define BUTTON_DOWN 4
#define BUTTON_LEFT 5
#define BUTTON_RIGHT 6
#define BUTTON_FIRE 7

void setup() {
  Serial.begin(9600);

  // Настраиваем пины как входы
  pinMode(BUTTON_UP, INPUT_PULLUP);
  pinMode(BUTTON_DOWN, INPUT_PULLUP);
  pinMode(BUTTON_LEFT, INPUT_PULLUP);
  pinMode(BUTTON_RIGHT, INPUT_PULLUP);
  pinMode(BUTTON_FIRE, INPUT_PULLUP);
}

void loop() {
  String message = "";

  if (digitalRead(BUTTON_UP) == LOW) {
    message += "1;";
  }
  if (digitalRead(BUTTON_DOWN) == LOW) {
    message += "2;";
  }
  if (digitalRead(BUTTON_LEFT) == LOW) {
    message += "3;";
  }
  if (digitalRead(BUTTON_RIGHT) == LOW) {
    message += "4;";
  }
  if (digitalRead(BUTTON_FIRE) == LOW) {
    message += "5;";
  }

  if (message.length() > 0) {
    Serial.println(message);
  }

  delay(100);

}

