const sliderContainer = document.getElementById('sliderContainer');

// Tablica z nazwami cech; TO ZMIENIC NA CECHY I PRZESKALOWAC JE NA 0 100
const cechy = [
  'Radosna',
  'Relaksacyjna',
  'Smutna',
  'Motywacyjna',
  'Romantyczna',
  'Zrelaksowana',
  'Energiczna',
  'Tajemnicza',
  'Zadziwiająca',
];

// Zmienna do przechowywania wartości aktywnych suwaków
const sliderValues = {};

// Pętla generująca suwaki z checkboxami
cechy.forEach((cecha, index) => {
  const id = index + 1;
  sliderContainer.innerHTML += `
    <div class="slidecontainer">
      <label>
        <input type="checkbox" class="slider-activation" id="activateSlider${id}" onchange="toggleSlider(${id})">
        Aktywuj
      </label>
      <p>${cecha}:</p>
      <input type="range" min="1" max="100" value="50" class="slider" id="myRange${id}" oninput="updateSliderVariable(${id})" disabled>
      <output id="valueOutput${id}">0</output>
    </div>
  `;
});

// Funkcja aktywująca/dezaktywująca suwaki
function toggleSlider(id) {
  const slider = document.getElementById(`myRange${id}`);
  const checkbox = document.getElementById(`activateSlider${id}`);

  if (checkbox.checked) {
    slider.disabled = false;
    sliderValues[`slider${id}`] = slider.value; // Dodaj suwak do obiektu
  } else {
    slider.disabled = true;
    delete sliderValues[`slider${id}`]; // Usuń suwak z obiektu
  }
}

// Funkcja aktualizująca zmienne
function updateSliderVariable(id) {
  const slider = document.getElementById(`myRange${id}`);
  const output = document.getElementById(`valueOutput${id}`);
  const checkbox = document.getElementById(`activateSlider${id}`);

  output.value = slider.value;

  // Aktualizuj wartość tylko jeśli checkbox jest zaznaczony
  if (checkbox.checked) {
    sliderValues[`slider${id}`] = slider.value;
  }
  console.log(sliderValues); // Wyświetl tylko aktywne wartości
}

// Funkcja wyświetlająca wartości aktywnych suwaków
function displaySliderValues() {
  const outputDiv = document.getElementById('sliderValuesOutput');
  outputDiv.innerHTML = JSON.stringify(sliderValues, null, 2); // Formatowanie obiektu jako tekst JSON
  console.log(sliderValues); // Wyświetl w konsoli
}
