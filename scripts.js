var tw = (function() {
  'use strict';

  var date = new Date();
  var hour = date.getHours();

  return {
    date: date,

    maptime: function() {
      var number = hour;

      $('main > *').each(function() {
        var element = $(this);

        element.attr('data-time', number++);
      });
    },

    coordinates: {
      latitude: null,
      longitude: null
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
      });
    } else {
      alert('Geolocation is not supported by this browser.');
    }
  }
});

$('form[name="itinerary"]').on({
  'submit': function(event) {
    var articles = $('main > article');
    var send = {
      env: 'dev'
    };

    if(articles.length) {
      articles.remove();
    }

    $.ajax({
      type: 'POST',
      url: 'https://us-central1-travelweather-1548474103293.cloudfunctions.net/travelweather-1',
      data: JSON.stringify(send),
      contentType: "application/json; charset=utf-8",
      dataType: 'json',
      crossDomain: true,
      success: function(get) {
        var footer = $('main > footer');
        var template = $('body > template').html();

        // console.log(get);

        $.each(get.hourly, function(index, hour) {
          var cloned = $(template);

          cloned.find('[data-fill]').each(function(index, item) {
            var fill = $(item).data('fill');

            switch(fill) {
              case 'time':
                $(item).html(tw.date.toLocaleTimeString('en-US'));
              break;

              case 'timezone':
                // $(item).html(hour.temp);
              break;

              case 'temperature':
                $(item).html(hour.temp);
              break;

              case 'location':
                // $(item).html(hour.temp);
              break;
            }
          });

          cloned.insertBefore(footer);
        });

        tw.maptime();

        $('button[name="route"]').text('Reroute');

        $('html, body').animate({
          'scrollTop': $('main > article:first-of-type').offset().top,
        }, 900, 'swing');
      }
    });

    event.preventDefault();
  }
});
