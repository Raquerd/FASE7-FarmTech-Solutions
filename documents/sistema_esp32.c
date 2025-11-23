// ===== Bibliotecas necessárias =====
#include <DHT.h>               // Biblioteca sensor DHT22
#include <Wire.h>              // Biblioteca I2C
#include <LiquidCrystal_I2C.h> // Biblioteca do LCD I2C

// ===== Definição dos pinos =====
#define PINO_FOSFORO 32   
#define PINO_POTASSIO 33  
#define PINO_PH 34        
#define PINO_DHT 4        
#define PINO_RELE 27      
#define PINO_LED 15       

// ===== Inicialização do DHT22 =====
#define DHTTYPE DHT22
DHT dht(PINO_DHT, DHTTYPE);

// ===== Inicialização do LCD I2C =====
LiquidCrystal_I2C lcd(0x27, 16, 2); // Endereço padrão I2C

// ===== Variáveis globais otimizadas =====
unsigned long tempoBombaLigada = 0;
bool bombaLigada = false;
const unsigned long DURACAO_IRRIGACAO = 30000; // 30 segundos

bool fosforoPresente = false;
bool potassioPresente = false;
bool ligarBomba = false;

uint16_t valorLDR = 0;  // pH em leitura bruta do ADC (0-4095)
float ph = 7.0;         // pH convertido
uint8_t umidade = 50;   // Umidade (%)
float temperatura = 25.0; // Temperatura em °C

// ==================================
void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(PINO_FOSFORO, INPUT_PULLUP);
  pinMode(PINO_POTASSIO, INPUT_PULLUP);
  pinMode(PINO_RELE, OUTPUT);
  pinMode(PINO_LED, OUTPUT);
  digitalWrite(PINO_RELE, HIGH); // Relé desligado no início
  digitalWrite(PINO_LED, LOW);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("Sistema iniciado");
  delay(2000);
  lcd.clear();
}

// ==================================
void loop() {
  lerSensores();
  processarLogicaIrrigacao();
  exibirNoSerial();
  exibirNoLCD();

  delay(3000);  // Tempo de ciclo completo
}

// ==================================
// Função para leitura dos sensores
void lerSensores() {
  // Leitura dos botões (inversão lógica pois usamos INPUT_PULLUP)
  fosforoPresente = !digitalRead(PINO_FOSFORO);
  potassioPresente = !digitalRead(PINO_POTASSIO);

  // Leitura do pH (simulado via LDR)
  valorLDR = analogRead(PINO_PH);
  ph = map(valorLDR, 0, 4095, 200, 1400) / 100.0;

  // Leitura do DHT22
  float leituraUmidade = dht.readHumidity();
  float leituraTemperatura = dht.readTemperature();

  if (!isnan(leituraUmidade)) {
    umidade = static_cast<uint8_t>(leituraUmidade);
  } else {
    Serial.println("Erro na leitura DHT22 (umidade). Usando 50%");
    umidade = 50;
  }

  if (!isnan(leituraTemperatura)) {
    temperatura = leituraTemperatura;
  } else {
    Serial.println("Erro na leitura DHT22 (temperatura). Usando 25°C");
    temperatura = 25.0;
  }
}

// ==================================
// Lógica de irrigação
void processarLogicaIrrigacao() {
  bool umidadeBaixa = umidade < 50;
  bool fosforoAusente = !fosforoPresente;
  bool potassioAusente = !potassioPresente;
  bool phRuim = (ph < 5.5 || ph > 7.5);

  ligarBomba = (umidadeBaixa || fosforoAusente || potassioAusente || phRuim);

  digitalWrite(PINO_LED, ligarBomba ? HIGH : LOW);

  if (ligarBomba && !bombaLigada) {
    digitalWrite(PINO_RELE, LOW); // Liga a bomba (nível baixo)
    tempoBombaLigada = millis();
    bombaLigada = true;
    Serial.println("BOMBA LIGADA (30s)");
  }

  if (bombaLigada && (millis() - tempoBombaLigada >= DURACAO_IRRIGACAO)) {
    digitalWrite(PINO_RELE, HIGH); // Desliga a bomba
    bombaLigada = false;
    Serial.println("BOMBA DESLIGADA (30s)");
  }
}

// ==================================
// Exibe as informações no LCD
void exibirNoLCD() {
  // Primeira tela: umidade e irrigação
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Umi:");
  lcd.print(umidade);
  lcd.print("%");

  lcd.setCursor(0, 1);
  lcd.print("Irrig:");
  lcd.print(ligarBomba ? "ON " : "OFF");

  delay(1000); // Mostra por 1 segundo

  // Segunda tela: pH e nutrientes
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("pH:");
  lcd.print(ph, 1);

  lcd.setCursor(8, 0);
  lcd.print("Fos:");
  lcd.print(fosforoPresente ? "OK" : "Nao");

  lcd.setCursor(0, 1);
  lcd.print("Pot:");
  lcd.print(potassioPresente ? "OK" : "Nao");

  delay(1000);
}

// ==================================
// Exibe as informações no monitor serial
void exibirNoSerial() {
  Serial.print("Fosforo: ");
  Serial.print(fosforoPresente ? "Presente" : "Ausente");

  Serial.print(" | Potassio: ");
  Serial.print(potassioPresente ? "Presente" : "Ausente");

  Serial.print(" | pH: ");
  Serial.print(ph, 2);

  Serial.print(" | Umidade: ");
  Serial.print(umidade);
  Serial.print("%");

  Serial.print(" | Temp: ");
  Serial.print(temperatura, 1);
  Serial.print("C");

  Serial.print(" -> Irrigacao ");
  Serial.println(ligarBomba ? "NECESSARIA" : "NAO NECESSARIA");

  // ===== Dados para Serial Plotter (umidade e temperatura) =====
  Serial.print(umidade);       // Primeiro valor
  Serial.print(" ");           // Separador
  Serial.println(temperatura); // Segundo valor

  Serial.println("------------------------");
}

