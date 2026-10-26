#include <SoftwareSerial.h>
#include <String.h>
#define NUM_DATOS 100
#define PRINT_INTERVAL_MS 33
#define INTERVAL_MS 17
#define EOG_PIN A0
#define RX_PIN 8
#define TX_PIN 9
#define SIGNAL_PIN 5
#define LED_PIN 6
// Pines del HC-05
#define MOVIL_MODE 1
#define STATIC_MODE 0
// EN ARDUINO UNO: pines 10 (RX) y 11 (TX)
SoftwareSerial BTSerial(RX_PIN, TX_PIN); // RX, TX
String inputBuffer = "";
unsigned long lastRequest = 0;
//const unsigned long INTERVAL_MS = 17; // ~60Hz en milisegundos
const float threshold = 0.1;
float bthFilter[NUM_DATOS];
int bthIndex;
float bthSuma;
float bthFilterValue;
bool conectado = false;
unsigned long lastDataTime = 0;
const unsigned long TIMEOUT = 3000; // 3 segundos sin datos = desconectado
unsigned long now;
char receivedChar;
int c1, c2;
float x, y, z;
float scalarValue;
//EOG
const float eogThreshold = 0.1;
float eogValue = 0;
float eogSuma = 0;
float eogFilterValue = 0.0f;
float eogFilter[NUM_DATOS];
int eogIndex = 0;
//Mensajes seriales
int msgReceived = 0;
int hasReacted = 0;
//Configuration
char serialRead;
const int ARRAY_LEN = 20;
char serialCharArray[ARRAY_LEN]; 
int auxiliar = 0;
float auxFloat = 0.0;
int vectorMaxSize = 0;
int thresholdMode = 0; // Referencia para threshold 0 Estatico / 1 Para que sea igual al promedio
int dataMode = 0; //0 for IMU, 1 for EOG
float thresholdIMU = 0.0;
float topThresholdEOG = 0.0;
float bottomThresholdEOG = 0.0;
float modTopEOG = 0.0;
float modBottomEOG = 0.0;
float currentTopThresholdEOG = 0.0;
float currentBottomThresholdEOG = 0.0;
float currentThresholdIMU = 0.0;
long lastSignalTime = 0.0;
long signalDuration = 1000;
bool isOn = false;

//Variables de impresion y frecuencia:
unsigned long lastPrint = 0;
unsigned long period = 0;
float freq = 0;
float printValue = 0.0;
float printPromedio = 0.0;
float printThreshold = 0.0;



void setup() {

  Serial.begin(9600);
  delay(1000);
  Serial.println("Iniciando conexion");
  BTSerial.begin(38400); 
  pinMode(EOG_PIN, INPUT);
  pinMode(SIGNAL_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  bthIndex = 0;
  eogIndex = 0;
  waitForMessages();
  Serial.print("vectorMaxSize: ");
  Serial.println(vectorMaxSize);
  for (int i = 0; i < vectorMaxSize; i++) 
  {
    bthFilter[i] = 0;
    eogFilter[i] = 0;
  }
  lastRequest = millis();
  lastDataTime = millis();
  lastPrint = millis();
  printValue = 0.0;
  printPromedio = 0.0;
  

}

void loop() {
  //readForMessages();
  turnOffSignal();
  
  if (dataMode == 0){
    reconectar();
    sendRequest();
    readBth();
  }
  else {
    readEOG();
  }

  printAt30Hz();
}

void readForMessages(){
  if (Serial.available()){
    if (msgReceived < 3){
      auxiliar = Serial.parseInt();
      Serial.println(auxiliar);
    }
    else {
      auxFloat = Serial.parseFloat();
      Serial.println(auxFloat);
    }
  
    switch (msgReceived){
      case 0: 
        vectorMaxSize = auxiliar;
        msgReceived++;
        break;
      case 1: 
        thresholdMode = auxiliar;
        msgReceived++;
        break;
      case 2:
        dataMode = auxiliar; 
        msgReceived++;
        break;
      case 3: 
        thresholdIMU = auxFloat;
        if (thresholdMode == STATIC_MODE){
          currentThresholdIMU = thresholdIMU;
        }
        msgReceived++;
        break;
      case 4: 
        modTopEOG = auxFloat;
        if (thresholdMode == STATIC_MODE){
          currentTopThresholdEOG = auxFloat;
        }
        msgReceived++;
        break;
      case 5: 
        modBottomEOG = auxFloat;
        if (thresholdMode == STATIC_MODE){
          currentBottomThresholdEOG = auxFloat;
        }
        msgReceived++;
        break;
    }


  }
}

void turnOffSignal(){
  if (millis()-lastSignalTime > signalDuration && isOn){
    digitalWrite(SIGNAL_PIN, 0);
    digitalWrite(LED_PIN, 0);
    isOn = false;
  }
}

void waitForMessages(){
  while (msgReceived < 6){
    readForMessages();
  }
}

void sendRequest(){
  now = millis();
  if (now - lastRequest >= INTERVAL_MS) {
    lastRequest = now;
    BTSerial.print(":41\n");
  }
}


void readEOG(){
  eogValue = analogRead(A0);
  eogSuma -= eogFilter[eogIndex];
  eogFilter[eogIndex] = eogValue;
  eogSuma += eogValue;
  eogIndex = (eogIndex + 1)%vectorMaxSize;
  eogFilterValue = eogSuma / vectorMaxSize;
  //Impresión
  printValue = eogValue;
  printPromedio = eogFilterValue;
  thresholdBeheaviorEOG();
}

void readBth(){
   while (BTSerial.available()) {
    receivedChar = BTSerial.read();
    lastDataTime = millis();
    if (!conectado) {
      conectado = true;
      Serial.println("Conectado!");
    }
    if (receivedChar == '\n') {
      inputBuffer.trim();
      if (inputBuffer.length() > 0 &&
          inputBuffer.indexOf(',') != -1 &&
          inputBuffer.lastIndexOf(',') != inputBuffer.indexOf(',')) {
        // Parsear x, y, z
        c1 = inputBuffer.indexOf(',');
        c2 = inputBuffer.lastIndexOf(',');
        x = inputBuffer.substring(0, c1).toFloat();
        y = inputBuffer.substring(c1 + 1, c2).toFloat();
        z = inputBuffer.substring(c2 + 1).toFloat();
        scalarValue = sqrt(z*z+y*y+x*x);
        if (x <= 1 && y <= 1 && z <= 1 && scalarValue <= 3.0)
        {
          bthSuma -= bthFilter[bthIndex];
          bthFilter[bthIndex] = scalarValue;
          bthSuma += scalarValue;
          bthIndex = (bthIndex+1) % vectorMaxSize;
          bthFilterValue = bthSuma/vectorMaxSize;
          //Impresión
          printValue = scalarValue;
          printPromedio = bthFilterValue;
          thresholdBeheaviorIMU();
        }
      }

      inputBuffer = "";

    } else if (receivedChar != '\r') {
      inputBuffer += receivedChar;
      if (inputBuffer.length() > 64) {
        inputBuffer = "";
      }
    }
  }
}

void reconectar(){
  if (conectado && (millis() - lastDataTime > TIMEOUT)) {
    Serial.println("Timeout: sin datos. Reconectando...");
    conectado = false;
    inputBuffer = "";
  }
}
void printAt30Hz(){
  now = millis();
  period = now - lastPrint;
  if (period >= PRINT_INTERVAL_MS){
    Serial.print(printValue, 5);
    Serial.print(",");
    Serial.print(printPromedio, 5);
    Serial.print(",");
    Serial.println(hasReacted);
    lastPrint = millis();
  }
}

void thresholdBeheaviorIMU(){
  if (thresholdMode == 1){
    currentThresholdIMU = bthFilterValue+thresholdIMU;
  }
  printThreshold = currentThresholdIMU;
  if (scalarValue >= currentThresholdIMU){  // 1 Threshold Movil
    
    digitalWrite(SIGNAL_PIN, 1);
    digitalWrite(LED_PIN, 1);
    lastSignalTime = millis();
    isOn = true;
    hasReacted = 1;
    
  }
  else
  {
    hasReacted = 0;
  }
}

void thresholdBeheaviorEOG(){
    if (thresholdMode == MOVIL_MODE){
      currentTopThresholdEOG = eogFilterValue+modTopEOG;
      currentBottomThresholdEOG = eogFilterValue-modBottomEOG;
    }
    printThreshold = currentTopThresholdEOG;

    if (eogValue <= currentBottomThresholdEOG || currentTopThresholdEOG <= eogValue ) {  // 1 Threshold Movil
      digitalWrite(SIGNAL_PIN, 1);
      digitalWrite(LED_PIN, 1);
      lastSignalTime = millis();
      isOn = true;
      hasReacted = 1;
    
    }
    else {
      hasReacted = 0;
    }


}
