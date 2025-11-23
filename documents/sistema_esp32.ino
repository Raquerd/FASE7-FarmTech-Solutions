{
  "version": 1,
  "author": "RM563588",
  "editor": "wokwi",
  "parts": [
    { "type": "board-esp32-devkit-c-v4", "id": "esp", "top": -48, "left": -81.56, "attrs": {} },
    {
      "type": "wokwi-pushbutton",
      "id": "btn1",
      "top": -15.8,
      "left": -239.8,
      "rotate": 180,
      "attrs": { "color": "green", "xray": "1", "bounce": "1", "key": "2" }
    },
    {
      "type": "wokwi-pushbutton",
      "id": "btn2",
      "top": 115.3,
      "left": -291.3,
      "rotate": 270,
      "attrs": { "color": "red", "xray": "1", "key": "1" }
    },
    {
      "type": "wokwi-dht22",
      "id": "dht1",
      "top": -182.1,
      "left": -63,
      "attrs": { "humidity": "53", "temperature": "29.5" }
    },
    { "type": "wokwi-relay-module", "id": "relay1", "top": 221, "left": -134.4, "attrs": {} },
    {
      "type": "wokwi-photoresistor-sensor",
      "id": "ldr1",
      "top": -265.6,
      "left": -316,
      "attrs": {}
    },
    {
      "type": "wokwi-led",
      "id": "led1",
      "top": -13.2,
      "left": 176.6,
      "attrs": { "color": "red" }
    },
    {
      "type": "wokwi-resistor",
      "id": "r1",
      "top": 80.75,
      "left": 115.2,
      "attrs": { "value": "1000" }
    },
    {
      "type": "wokwi-lcd1602",
      "id": "lcd1",
      "top": -176,
      "left": 120.8,
      "attrs": { "pins": "i2c" }
    }
  ],
  "connections": [
    [ "esp:TX", "$serialMonitor:RX", "", [] ],
    [ "esp:RX", "$serialMonitor:TX", "", [] ],
    [ "dht1:VCC", "esp:3V3", "red", [ "v0" ] ],
    [ "dht1:GND", "esp:GND.2", "black", [ "v0" ] ],
    [ "esp:4", "dht1:SDA", "purple", [ "h0" ] ],
    [ "relay1:IN", "esp:27", "white", [ "h-172.8", "v-38.6" ] ],
    [ "relay1:VCC", "esp:5V", "red", [ "h-9.6", "v-28.8", "h268.8", "v-57.6" ] ],
    [
      "relay1:GND",
      "esp:GND.3",
      "black",
      [ "h-19.2", "v-48.4", "h201.6", "v-144", "h-19.2", "v-19.2" ]
    ],
    [ "ldr1:VCC", "esp:3V3", "#8f4814", [ "h0" ] ],
    [ "ldr1:GND", "esp:GND.2", "white", [ "h0" ] ],
    [ "esp:34", "ldr1:AO", "gray", [ "h0" ] ],
    [ "led1:C", "r1:2", "cyan", [ "v0" ] ],
    [ "r1:1", "esp:GND.3", "cyan", [ "v0" ] ],
    [ "led1:A", "esp:15", "yellow", [ "v0" ] ],
    [ "btn1:2.l", "esp:32", "red", [ "h0" ] ],
    [ "btn2:1.r", "esp:33", "green", [ "v0" ] ],
    [ "btn1:2.r", "esp:GND.1", "magenta", [ "h-19.4", "v57.4", "h163.2", "v48" ] ],
    [ "btn2:1.l", "esp:GND.1", "blue", [ "v19.2", "h57.6", "v-76.8", "h134.25" ] ],
    [ "esp:21", "lcd1:SDA", "orange", [ "h86.4", "v-153.8" ] ],
    [ "lcd1:SCL", "esp:22", "green", [ "h-67.2", "v163.5", "h-38.4" ] ],
    [ "esp:3V3", "lcd1:VCC", "purple", [ "h-47.85", "v-172.8", "h162.9", "v57.5" ] ],
    [ "esp:GND.2", "lcd1:GND", "violet", [ "h28.8", "v-144", "h67.2", "v19.2" ] ]
  ],
  "dependencies": {}
}