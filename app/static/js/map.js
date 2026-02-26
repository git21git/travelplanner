/**
 * Скрипт для работы с Яндекс.Картами
 */

let map;
let placemarks = [];
let clusterer;

// Инициализация карты
function initMap(elementId, center = [55.751574, 37.573856], zoom = 10) {
  if (!ymaps) {
    console.error("Yandex Maps API not loaded");
    return;
  }

  map = new ymaps.Map(elementId, {
    center: center,
    zoom: zoom,
    controls: ["zoomControl", "typeSelector", "fullscreenControl"],
  });

  return map;
}

// Добавление метки на карту
function addPlacemark(lat, lng, options = {}) {
  if (!map) {
    console.error("Map not initialized");
    return null;
  }

  const placemark = new ymaps.Placemark(
    [lat, lng],
    {
      hintContent: options.hint || "",
      balloonContent: createBalloonContent(options),
    },
    {
      preset: options.preset || "islands#icon",
      iconColor: options.color || "#0d6efd",
    },
  );

  map.geoObjects.add(placemark);

  placemarks.push({
    id: options.id || Date.now(),
    placemark: placemark,
    data: options,
  });

  return placemark;
}

// Создание содержимого балуна
function createBalloonContent(options) {
  let content = `
        <div class="placemark-popup">
            <h6>${options.name || "Место"}</h6>
    `;

  if (options.address) {
    content += `<p><small>${options.address}</small></p>`;
  }

  if (options.notes) {
    content += `<p><small class="text-muted">${options.notes}</small></p>`;
  }

  content += `</div>`;

  return content;
}

// Удаление всех меток
function clearPlacemarks() {
  if (!map) return;

  placemarks.forEach((item) => {
    map.geoObjects.remove(item.placemark);
  });

  placemarks = [];

  if (clusterer) {
    map.geoObjects.remove(clusterer);
    clusterer = null;
  }
}

// Добавление кластеризатора
function enableClustering() {
  if (!map) return;

  clusterer = new ymaps.Clusterer({
    preset: "islands#invertedVioletClusterIcons",
    groupByCoordinates: false,
    clusterDisableClickZoom: false,
    clusterHideIconOnBalloonOpen: false,
    geoObjectHideIconOnBalloonOpen: false,
  });

  map.geoObjects.add(clusterer);
  return clusterer;
}

// Центрирование карты на метке
function centerOnPlacemark(placemarkId, zoom = 15) {
  const placemark = placemarks.find((p) => p.id === placemarkId);

  if (placemark && map) {
    const coords = placemark.placemark.geometry.getCoordinates();
    map.setCenter(coords, zoom, {
      duration: 300,
    });

    // Открываем балун
    placemark.placemark.balloon.open();
  }
}

// Поиск места по адресу
async function searchAddress(address) {
  if (!ymaps) {
    throw new Error("Yandex Maps API not loaded");
  }

  try {
    const result = await ymaps.geocode(address);
    const firstGeoObject = result.geoObjects.get(0);

    if (firstGeoObject) {
      const coords = firstGeoObject.geometry.getCoordinates();
      const name = firstGeoObject.properties.get("name");
      const description = firstGeoObject.properties.get("description");

      return {
        lat: coords[0],
        lng: coords[1],
        name: name,
        address: description,
      };
    }
  } catch (error) {
    console.error("Geocoding error:", error);
    throw error;
  }

  return null;
}

// Экспорт функций
window.TravelPlannerMap = {
  init: initMap,
  addPlacemark: addPlacemark,
  clear: clearPlacemarks,
  centerOn: centerOnPlacemark,
  searchAddress: searchAddress,
  enableClustering: enableClustering,
};
