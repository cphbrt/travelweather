var tw = (function() {
  'use strict';

  var date = new Date();
  var hour = date.getHours();

  return {
    'maptime': function() {
      $('main > *').each(function() {
        var element = $(this);

        element.attr('data-time', hour++);
      });
    },
    'coordinates': {
      'latitude': null,
      'longitude': null
    }
  };
}());

$(function() {
  tw.maptime();
});

$('button[name="coordinates"]').on({
  'click': function() {
    if(navigator.geolocation) {
      var input = $('input[name="origin"]');

      input.prop('disabled', true);

      navigator.geolocation.getCurrentPosition(function(position) {
        input.prop('disabled', false).val('Your Location');

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
      var template = $('body > template').clone();

      console.log(get);
    });

    event.preventDefault();
  }
});
