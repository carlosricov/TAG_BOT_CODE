#include "FastLED.h"
#include <QMC5883LCompass.h>      //ADDED (Eric)
#include <Wire.h>                 //ADDED (Eric)

#define DriveA 10
#define DriveB 11
#define DriveC 9

#define DirectionA 13
#define DirectionB 12
#define DirectionC 8

// Motor A Gain
#define MotorA_Gain_x 0
#define MotorA_Gain_y 0.66666
#define MotorA_Gain_w 0.33333

// Motor B Gain
//#define MotorB_Gain_x -0.57735
//#define MotorB_Gain_y -0.33333
#define MotorB_Gain_x -0.58
#define MotorB_Gain_y -0.34
#define MotorB_Gain_w 0.33333

// Motor C Gain
//#define MotorC_Gain_x 0.57735
//#define MotorC_Gain_y -0.33333
#define MotorC_Gain_x 0.58
#define MotorC_Gain_y -0.34
#define MotorC_Gain_w 0.33333

// Compass                        //ADDED (Eric) [2 lines]
QMC5883LCompass compass;
int ref = 0;
int compcount = 0;

// Buzzer & Lights.
#define BUZZ 3
#define PIEZO A3

// Addressable LED data pin.
#define LED 6

double MotorA_Speed = 0;
double MotorB_Speed = 0;
double MotorC_Speed = 0;

double x_gain = 0;
double y_gain = 0;
double w_gain = 0;

// Game mode state.
int gameMode = 0;
long int tim = -1;
boolean firstTimeInMode = true;

unsigned long int pastTime = 0;
unsigned long int currTime = 0;

// For Wack-a-mole mode.
unsigned long int pastLightTime = 0;
unsigned long int currLightTime = 0;
boolean ledsAreOn = false;

// To accomodate debounce issue.
unsigned long int pastHitTime = 0;
unsigned long int currHitTime = 0;

// Orientation timer.
unsigned long int pastOriTime = 0;
unsigned long int currOriTime = 0;

// Not implemented.
boolean debounce = false;

// LED count.
const int numLEDS = 9;

// Piezo threshold.
const int threshold = 100;

// Store the impact and track how many times impacted.
int sensorReading = 0;
int state = 0;
int counter = 0;

CRGB leds[numLEDS];

double oldMag = 0;
boolean justOri = false;

void Blue() 
{                     // ADDED this function (Eric)
  // Blue LED's
  leds[1] = CRGB::Blue;
  leds[4] = CRGB::Blue;
  leds[7] = CRGB::Blue;
  FastLED.show();
}

void Green() 
{                    // ADDED this function (Eric)
  // Green LED's
  leds[1] = CRGB::Red;
  leds[4] = CRGB::Red;
  leds[7] = CRGB::Red;
  FastLED.show();
}

//Compass initial position setup.
void CompassInitPOS() 
{

  int x, y, z, a, b;
  char myArray[3];

  // Read input from compass and store values.
  compass.read();
  x = compass.getX();
  y = compass.getY();
  z = compass.getZ();

  // Set initial bearing.
  a = compass.getAzimuth();
  b = compass.getBearing(a);
  ref = b;

  // Display direction text *FOR DEBUGGING*
  compass.getDirection(myArray, a);

  DeriveGain (0, 0, 0);
  Drive();

  Blue();
  delay(1000);
  FastLED.clear();
  FastLED.show();
}

void Compass() 
{
  bool aligned = false;

  // Align the TAG Bot.
  while (aligned != true) 
  {
    int x, y, z, a, b;
    char myArray[3];

    compass.read();

    x = compass.getX();
    y = compass.getY();
    z = compass.getZ();

    a = compass.getAzimuth();
    b = compass.getBearing(a);

    compass.getDirection(myArray, a);

    if (b == ref) 
    {
      aligned = true;
      DeriveGain (0, 0, 0);
    }
    else if ((b - (ref + 8) % 16) >= 0) 
    {
      DeriveGain (0, 0, 0.6);
    }
    else if ((b - (ref + 8) % 16) < 0) 
    {
      DeriveGain (0, 0, -0.6);
    }
    
    Drive();
  }
  
  // LED display for testing.
  //Green();
  //delay(1000);
  //FastLED.clear();
  //FastLED.show();
}

void DeriveGain(double X, double Y, double W) 
{
  double MotorA_Gain = MotorA_Gain_x * X + MotorA_Gain_y * Y + MotorA_Gain_w * W;
  double MotorB_Gain = MotorB_Gain_x * X + MotorB_Gain_y * Y + MotorB_Gain_w * W;
  double MotorC_Gain = MotorC_Gain_x * X + MotorC_Gain_y * Y + MotorC_Gain_w * W;

  MotorA_Speed = map(MotorA_Gain * 100, -100, 100, -255, 255);
  MotorB_Speed = map(MotorB_Gain * 100, -100, 100, -255, 255);
  MotorC_Speed = map(MotorC_Gain * 100, -100, 100, -255, 255);
}

void Drive() 
{
  //Motor A direction setup
  if ( MotorA_Speed > 0) 
  {
    digitalWrite(DirectionA, LOW);
  }
  else 
  {
    digitalWrite(DirectionA, HIGH);
  }

  //Motor B direction setup
  if (MotorB_Speed > 0) 
  {
    digitalWrite(DirectionB, LOW);
  }
  else 
  {
    digitalWrite(DirectionB, HIGH);
  }

  //Motor C direction setup
  if (MotorC_Speed > 0) 
  {
    digitalWrite(DirectionC, LOW);
  }
  else 
  {
    digitalWrite(DirectionC, HIGH);
  }

  //Motor Drive
  analogWrite(DriveA, abs(MotorA_Speed));
  analogWrite(DriveB, abs(MotorB_Speed));
  analogWrite(DriveC, abs(MotorC_Speed));
}


void setup() 
{
  // 9600 baudrate for Bluetooth.
  Serial.begin(9600);

  // Motor setup.
  pinMode(DriveA, OUTPUT);
  pinMode(DriveB, OUTPUT);
  pinMode(DriveC, OUTPUT);
  pinMode(DirectionA, OUTPUT);
  pinMode(DirectionB, OUTPUT);
  pinMode(DirectionC, OUTPUT);

  // Compass setup
  Wire.begin();
  compass.init();

  // Buzzer setup
  pinMode(BUZZ, OUTPUT);
  noTone(BUZZ);

  pinMode(PIEZO, INPUT);

  // Addressable LED setup.
  FastLED.addLeds<WS2812B, LED>(leds, numLEDS);

  DeriveGain (0, 0, 0);

  // Compass initialization for heading read and stored
  CompassInitPOS();
}

void loop() 
{
  sensorReading = analogRead(PIEZO);

  if (Serial.available() > 0) 
  {
    String data = Serial.readString();
    int index = data.indexOf(',');
    double magnitude = data.substring(0, index).toDouble();
    double dir = data.substring(index + 1).toDouble();

    // Negative magnitudes indicate change of game mode.
    if (magnitude < 0) 
    {
      // Update mode w/ timer and stop motors.
      gameMode = magnitude;
      DeriveGain(0, 0, 0);

      // Timer will have a set 2 minute timer.
      tim = (gameMode == -2) ? 120 : int(dir);

      // Reset values.
      state = 0;
      firstTimeInMode = true;
      pastLightTime = 0;
      currLightTime = 0;
      pastHitTime = 0;
      currHitTime = 0;

      // Indicate to user that the mode was updated.
      if (gameMode == -1) 
      {
        tone(BUZZ, 1500, 500);
      }
      else if (gameMode == -2) 
      {
        tone(BUZZ, 2000, 500);
      }
      else if (gameMode == -3) 
      {
        tone(BUZZ, 5000, 500);
      }
      else if (gameMode == -4) 
      {
        tone(BUZZ, 8500, 500);
      }

      FastLED.clear();
      FastLED.show();
    }

    magnitude /= 100;

    x_gain = (magnitude * cos(dir));
    y_gain = (magnitude * sin(dir));

    if (magnitude > 0 && gameMode < 0) 
    { 
      // All Drive
      DeriveGain(x_gain, y_gain, 0);
      //currOriTime = millis();

      if (gameMode <= -2) 
      {
        if (!checkTimer()) 
        {
          // Reset user mode.
          gameMode = 0;

          // Stop motors.
          DeriveGain(0, 0, 0);

          // Reset sensor reading.
          sensorReading = 0;

          // Reset hit counter.
          counter = 0;

          // Reset piezo state.
          state = 0;

          // Play stop indicator tone.
          tone(BUZZ, 1000, 1000);

          // Turn off LEDs.
          FastLED.clear();
          FastLED.show();
        }
        // Basic game mode with set 2 minute timer.
        else if (gameMode == -2) 
        {
          currHitTime = millis();

          // Check for impact & account for debounce.
          if (sensorReading >= threshold && (currHitTime - pastHitTime > 1500)) 
          {
            pastHitTime = millis();

            // Track hit.
            state++;

            // Check hit count.
            if (state == 1) 
            {
              // Turn on lower level LEDs.
              leds[0] = CRGB::Blue;
              leds[3] = CRGB::Blue;
              leds[6] = CRGB::Blue;

              // Turn on LEDs and play indicator.
              FastLED.show();
            }
            else if (state == 2) 
            {
              // Turn on mid level LEDs.
              leds[1] = CRGB::Red;
              leds[4] = CRGB::Red;
              leds[7] = CRGB::Red;

              FastLED.show();
            }
            else if (state == 3) 
            {
              // Turn on top level LEDs.
              leds[2] = CRGB::Green;
              leds[3] = CRGB::Green;
              leds[6] = CRGB::Green;

              FastLED.show();
            }
            else if (state == 4) 
            {
              // Reset.
              FastLED.clear();
              FastLED.show();

              state = 0;
            }
          }
        }
        // This user mode sends a confirmed hit to the pi.
        else if (gameMode == -3) 
        {
          currHitTime = millis();
          // Check for impact & account for debounce.
          if (sensorReading >= threshold && (currHitTime - pastHitTime > 1500)) 
          {
            pastHitTime = millis();

            state++;

            // Send to the Pi that a hit was detected.
            Serial.println(1);

            // Check hit count.
            if (state == 1) 
            {
              // Turn on lower level LEDs.
              leds[0] = CRGB::Blue;
              leds[3] = CRGB::Blue;
              leds[6] = CRGB::Blue;

              FastLED.show();
            }
            else if (state == 2) {
              // Turn on mid level LEDs.
              leds[1] = CRGB::Red;
              leds[4] = CRGB::Red;
              leds[7] = CRGB::Red;

              FastLED.show();
            }
            else if (state == 3) 
            {
              // Turn on top level LEDs.
              leds[2] = CRGB::Green;
              leds[5] = CRGB::Green;
              leds[8] = CRGB::Green;

              FastLED.show();
            }
            else if (state == 4) 
            {
              // Reset.
              FastLED.clear();
              FastLED.show();

              state = 0;
            }
          }
        }
        else if (gameMode == -4) 
        {
          // Start led timer if the leds are off.
          if (!ledsAreOn) 
          {
            pastLightTime = millis();
          }

          // Turn on LEDs.
          if (currLightTime - pastLightTime <= 10000 && !ledsAreOn) 
          {
            // Start tracking how long lights been on.
            pastLightTime = millis();

            ledsAreOn = true;

            // Turn on all LEDs.
            leds[0] = CRGB::Red;
            leds[4] = CRGB::Blue;
            leds[8] = CRGB::Green;

            leds[2] = CRGB::Red;
            leds[6] = CRGB::Blue;
            leds[10] = CRGB::Green;

            leds[1] = CRGB::Red;
            leds[5] = CRGB::Blue;
            leds[9] = CRGB::Green;

            FastLED.show();
          }

          currLightTime = millis();

          // 10 second window that the user can hit the TAG Bot.
          if (ledsAreOn && (currLightTime - pastLightTime <= 10000)) 
          {
            currHitTime = millis();
            if (sensorReading >= threshold && (currHitTime - pastHitTime > 1500)) 
            {
              pastHitTime = millis();
              // Send register hit
              Serial.println(1);
            }
          }

          // 10 second window that the LEDs are off.
          if (ledsAreOn && (currLightTime - pastLightTime > 10000)) 
          {
            FastLED.clear();
            FastLED.show();
          }

          // After total 20 seconds, repeat process.
          if (currLightTime - pastLightTime > 15000) 
          {
            ledsAreOn = false;
            pastLightTime = 0;
            currLightTime = 0;
          }
        }
      }
      else if (gameMode == -1) 
      {
        currHitTime = millis();

        // Check for impact & account for debounce.
        if (sensorReading >= threshold && (currHitTime - pastHitTime > 1500)) 
        {
          pastHitTime = millis();

          state++;

          // Send to the Pi that a hit was detected.
          Serial.println(1);

          // Check hit count.
          if (state == 1) 
          {
            // Turn on lower level LEDs.
            leds[0] = CRGB::Blue;
            leds[3] = CRGB::Blue;
            leds[6] = CRGB::Blue;

            FastLED.show();
          }
          else if (state == 2) 
          {
            // Turn on mid level LEDs.
            leds[1] = CRGB::Red;
            leds[4] = CRGB::Red;
            leds[7] = CRGB::Red;

            FastLED.show();
          }
          else if (state == 3) {
            // Turn on top level LEDs.
            leds[2] = CRGB::Green;
            leds[5] = CRGB::Green;
            leds[8] = CRGB::Green;

            FastLED.show();
          }
          else if (state == 4) {
            // Reset.
            FastLED.clear();
            FastLED.show();

            state = 0;
          }
        }
      }
    }
    else if (magnitude == 0) 
    {
      // Indicate stop.
      tone(BUZZ, 1000, 250);

      // Stop motors.
      DeriveGain(0, 0, 0);

      // Reset
      gameMode = 0;
      tim = -1;
      state = 0;
      firstTimeInMode = true;
      pastLightTime = 0;
      currLightTime = 0;
      pastHitTime = 0;
      currHitTime = 0;

      // Turn off LEDs.
      FastLED.clear();
      FastLED.show();
    }
  }
  else 
  {
    if (millis() - pastOriTime > 500)
    {
      Compass();
      pastOriTime = millis();
 
      DeriveGain(x_gain,y_gain,0);
    }
        
    if (gameMode <= -2) 
    {
      if (!checkTimer()) 
      {
        // Reset user mode.
        gameMode = 0;

        // Stop motors.
        DeriveGain(0, 0, 0);

        // Reset sensor reading.
        sensorReading = 0;

        // Reset hit counter.
        counter = 0;

        // Reset piezo state.
        state = 0;

        // Play stop indicator tone.
        tone(BUZZ, 1000, 1000);

        // Turn off LEDs.
        FastLED.clear();
        FastLED.show();
      }
      // Basic game mode.
      else if (gameMode == -2) 
      {
        currHitTime = millis();

        // Check for impact & account for debounce.
        if (sensorReading >= threshold && (currHitTime - pastHitTime > 1500)) 
        {
          pastHitTime = millis();
          state++;

          // Check hit count.
          if (state == 1) 
          {
            // Turn on lower level LEDs.
            leds[0] = CRGB::Blue;
            leds[3] = CRGB::Blue;
            leds[6] = CRGB::Blue;

            FastLED.show();
          }
          else if (state == 2) 
          {
            // Turn on mid level LEDs.
            leds[1] = CRGB::Red;
            leds[4] = CRGB::Red;
            leds[7] = CRGB::Red;

            FastLED.show();
          }
          else if (state == 3) 
          {
            // Turn on top level LEDs.
            leds[2] = CRGB::Green;
            leds[5] = CRGB::Green;
            leds[8] = CRGB::Green;

            // Turn on LEDs and play indicator.
            FastLED.show();
          }
          else if (state == 4) 
          {
            // Reset.
            FastLED.clear();
            FastLED.show();

            state = 0;
          }
        }
      }
      else if (gameMode == -3) 
      {
        currHitTime = millis();

        // Check for impact & account for debounce.
        if (sensorReading >= threshold && (currHitTime - pastHitTime > 1500)) 
        {
          pastHitTime = millis();
          state++;

          // Send to the Pi that a hit was detected.
          Serial.println(1);

          // Check hit count.
          if (state == 1) 
          {
            // Turn on lower level LEDs.
            leds[0] = CRGB::Blue;
            leds[3] = CRGB::Blue;
            leds[6] = CRGB::Blue;

            FastLED.show();
          }
          else if (state == 2) 
          {
            // Turn on mid level LEDs.
            leds[1] = CRGB::Red;
            leds[4] = CRGB::Red;
            leds[7] = CRGB::Red;

            FastLED.show();
          }
          else if (state == 3) 
          {
            // Turn on top level LEDs.
            leds[2] = CRGB::Green;
            leds[5] = CRGB::Green;
            leds[8] = CRGB::Green;

            // Turn on LEDs and play indicator.
            FastLED.show();
          }
          else if (state == 4) 
          {
            // Reset.
            FastLED.clear();
            FastLED.show();

            state = 0;
          }
        }
      }
      else if (gameMode == -4) 
      {
        if (!ledsAreOn) 
        {
          pastLightTime = millis();
        }

        // Turn on LEDs.
        if (currLightTime - pastLightTime <= 10000 && !ledsAreOn) 
        {
          // Start tracking how long lights been on.
          pastLightTime = millis();

          ledsAreOn = true;

          // Turn on all LEDs.
          leds[0] = CRGB::Red;
          leds[4] = CRGB::Blue;
          leds[8] = CRGB::Green;

          leds[2] = CRGB::Red;
          leds[6] = CRGB::Blue;
          leds[10] = CRGB::Green;

          leds[1] = CRGB::Red;
          leds[5] = CRGB::Blue;
          leds[9] = CRGB::Green;

          FastLED.show();
        }

        currLightTime = millis();

        if (ledsAreOn && (currLightTime - pastLightTime <= 10000)) 
        {
          currHitTime = millis();
          if (sensorReading >= threshold && (currHitTime - pastHitTime > 1500)) 
          {
            pastHitTime = millis();
            // Send register hit
            Serial.println(1);
          }
        }

        if (ledsAreOn && (currLightTime - pastLightTime > 10000)) 
        {
          FastLED.clear();
          FastLED.show();
        }

        if (currLightTime - pastLightTime > 15000) 
        {
          ledsAreOn = false;
          pastLightTime = 0;
          currLightTime = 0;
        }
      }
    }
    else if (gameMode == -1) 
    {
      currHitTime = millis();

      // Check for impact.
      if (sensorReading >= threshold && (currHitTime - pastHitTime > 1500)) 
      {
        pastHitTime = millis();
        state++;

        // Send to the Pi that a hit was detected.
        Serial.println(1);

        // Check hit count.
        if (state == 1) 
        {
          // Turn on lower level LEDs.
          leds[0] = CRGB::Blue;
          leds[3] = CRGB::Blue;
          leds[6] = CRGB::Blue;
          FastLED.show();
        }
        else if (state == 2) 
        {
          // Turn on mid level LEDs.
          leds[1] = CRGB::Red;
          leds[4] = CRGB::Red;
          leds[7] = CRGB::Red;

          FastLED.show();
        }
        else if (state == 3) 
        {
          // Turn on top level LEDs.
          leds[2] = CRGB::Green;
          leds[5] = CRGB::Green;
          leds[8] = CRGB::Green;

          FastLED.show();
        }
        else if (state == 4) 
        {
          // Reset.
          FastLED.clear();
          FastLED.show();

          state = 0;
        }
      }
    }
  }
  Drive();
  
  if (compcount % 2 == 0 && compcount != 0) 
  {          // ADDED (Eric)[2 Lines]
    Compass();
  }
}

boolean checkTimer() 
{
  if (firstTimeInMode) 
  {
    // Avoid overflow.
    pastTime = millis() / 1000;

    firstTimeInMode = false;
  }

  // Avoid overflow.
  currTime = millis() / 1000;

  // Expired time.
  if (currTime - pastTime <= tim) 
  {
    return true;
  }
  else 
  {
    // Reset variables & stop motors.
    gameMode = 0;
    DeriveGain(0, 0, 0);
    Drive();
    
    if (compcount % 2 == 0 && compcount != 0) 
    {          // ADDED (Eric)[2 Lines]
      Compass();
    }

    tim = -1;

    firstTimeInMode = true;

    pastLightTime = 0;
    currLightTime = 0;
    pastHitTime = 0;
    currHitTime = 0;

    //Serial.println(1);

    return false;
  }
}
