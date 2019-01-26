var tw = (function() {
  'use strict';

  return {
    'coordinates': {
      'latitude': null,
      'longitude': null
    }
  };
}());

$('button[name="coordinates"]').on({
  'click': function() {
    if(navigator.geolocation) {
      var input = $('input[name="origin"]');

      navigator.geolocation.getCurrentPosition(function(position) {
        input.val('Your Location');

        tw.coordinates.latitude = position.coords.latitude;
        tw.coordinates.longitude = position.coords.longitude;
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
    var post = {
      'env': 'dev'
    }

    $.post({
      url: 'https://us-central1-travelweather-1548474103293.cloudfunctions.net/travelweather-1',
      data: post
    }, function(get) {
      console.log(get);
    });

    event.preventDefault();
  }
});
