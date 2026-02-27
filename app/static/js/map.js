/**
 * Скрипт для работы с Яндекс.Картами
 */

let map;
let placemarks = [];
let clusterer;

// Инициализация карты
function initYandexMap(elementId, center = [55.751574, 37.573856], zoom = 10) {
  return new Promise((resolve, reject) => {
    if (!window.ymaps) {
      reject(new Error("Yandex Maps API not loaded"));
      return;
    }

    ymaps.ready(() => {
      try {
        map = new ymaps.Map(elementId, {
          center: center,
          zoom: zoom,
          controls: ["zoomControl", "typeSelector", "fullscreenControl"],
        });

        // Добавляем кластеризатор
        clusterer = new ymaps.Clusterer({
          preset: "islands#invertedVioletClusterIcons",
          groupByCoordinates: false,
          clusterDisableClickZoom: false,
          clusterHideIconOnBalloonOpen: false,
          geoObjectHideIconOnBalloonOpen: false,
        });

        map.geoObjects.add(clusterer);
        resolve(map);
      } catch (error) {
        reject(error);
      }
    });
  });
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
      hintContent: options.name || "",
      balloonContent: createBalloonContent(options),
      id: options.id,
    },
    {
      preset: options.preset || "islands#blueIcon",
      iconColor: options.color || "#0d6efd",
      draggable: options.draggable || false,
    },
  );

  // Сохраняем данные метки
  const placemarkData = {
    id: options.id || Date.now(),
    placemark: placemark,
    data: options,
  };

  placemarks.push(placemarkData);

  // Добавляем в кластеризатор
  clusterer.add(placemark);

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

  // Добавляем кнопки действий, если есть id
  if (options.id) {
    content += `
            <div class="mt-2">
                <a href="/places/${options.id}/edit" class="btn btn-sm btn-outline-primary me-1">
                    <i class="bi bi-pencil"></i>
                </a>
                <button onclick="deletePlace(${options.id})" class="btn btn-sm btn-outline-danger">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
  }

  content += `</div>`;
  return content;
}

// Удаление всех меток
function clearPlacemarks() {
  if (!map || !clusterer) return;

  clusterer.removeAll();
  placemarks = [];
}

// Удаление конкретной метки
function removePlacemark(placemarkId) {
  const index = placemarks.findIndex((p) => p.id === placemarkId);
  if (index !== -1) {
    clusterer.remove(placemarks[index].placemark);
    placemarks.splice(index, 1);
  }
}

// Центрирование карты на метке
function centerOnPlacemark(placemarkId, zoom = 15) {
  const placemarkData = placemarks.find((p) => p.id === placemarkId);

  if (placemarkData && map) {
    const coords = placemarkData.placemark.geometry.getCoordinates();
    map.setCenter(coords, zoom, {
      duration: 300,
    });

    // Открываем балун
    placemarkData.placemark.balloon.open();
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
        address: description || address,
      };
    }
  } catch (error) {
    console.error("Geocoding error:", error);
    throw error;
  }

  return null;
}

// Получение текущего центра карты
function getMapCenter() {
  return map ? map.getCenter() : null;
}

// Получение текущего зума
function getMapZoom() {
  return map ? map.getZoom() : null;
}

// Экспорт функций
window.TravelPlannerMap = {
  init: initYandexMap,
  addPlacemark: addPlacemark,
  clear: clearPlacemarks,
  remove: removePlacemark,
  centerOn: centerOnPlacemark,
  searchAddress: searchAddress,
  getCenter: getMapCenter,
  getZoom: getMapZoom,
};
