var tw = (function() {
  'use strict';

  return {
    'coordinates': {
      'latitude': null,
      'longitude': null
    }
  };
}());

// var x = document.getElementById("demo");
//
// function getLocation() {
//   if(navigator.geolocation) {
//     navigator.geolocation.getCurrentPosition(showPosition);
//   } else {
//     x.innerHTML = "Geolocation is not supported by this browser.";
//   }
// }
//
// function showPosition(position) {
//   x.innerHTML = "Latitude: " + position.coords.latitude + "<br>Longitude: " + position.coords.longitude;
// }
//
// var lad = position.coords.latitude;
// var log = position.coords.longitude;

$('button[name="coordinates"]').on({
  'click': function() {
    if(navigator.geolocation) {
      var input = $('input[name="origin"]');

      navigator.geolocation.getCurrentPosition(function(position) {
        input.val('Your Location');

        tw.coordinates.latitude = position.coords.latitude;
        tw.coordinates.longitude = position.coords.longitude;

        alert('tw.coordinates.latitude');
      }, function() {
        alert('FAIL');
      });
    } else {
      alert('Geolocation is not supported by this browser.');
    }
  }
});

$('form[name="itinerary"]').on({
  'submit': function(event) {
    $.ajax({
      type: 'POST',
      url: 'https://us-central1-travelweather-1548474103293.cloudfunctions.net/travelweather-1',
      data: {
        'environment': 'development'
      },
      // dataType: 'jsonp',
    }, function(data) {
      console.log(data);
    });

    event.preventDefault();
  }
});
