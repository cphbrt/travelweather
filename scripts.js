var tw = (function() {
  'use strict';

  var env = 'dev';
  var date = new Date();
  var hour = date.getHours();

  return {
    date: date,

    logo: $('div[id="logo"]'),

    mapicon: function(name) {
      $('img[data-icon]').each(function() {
        var element = $(this);
        var name = $(this).data('icon');

        $.get('images/' + name + '.svg', function(svg) {
          element.replaceWith(svg);
        }, 'text');
      });
    },

    maptime: function() {
      var number = hour;

      $('body').attr('data-time', number);

      $('main > *').each(function() {
        var element = $(this);

        if(number == 25 || number == 0) {
          number = 1;
        }

        element.attr('data-time', number++);
      });
    },

    scrolly: function() {
      var element = $('main > header');

      $('html, body').animate({
        'scrollTop': element.offset().top + element.outerHeight(),
      }, 900, 'swing');
    },

    collection: {
      env: env,
      origin: null,
      destination: null,
      method: null
    },

    coordinates: {
      latitude: false,
      longitude: false
    }
  };
}());

$(function() {
  tw.mapicon();
  tw.maptime();
});

$('button[name="coordinates"]').on({
  'click': function() {
    if(navigator.geolocation) {
      var input = $('input[name="origin"]');

      input.prop('disabled', true);

      tw.logo.addClass('loading');

      navigator.geolocation.getCurrentPosition(function(position) {
        input.prop('disabled', false).val('Your Location');

        tw.logo.removeClass('loading');

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
    var submit = $('button[name="route"]');
    var articles = $('main > article');
    var formData = new FormData(this);
    var sendData = {
      env: tw.collection.env,
      start_location: formData.get('origin').trim(),
      end_location: formData.get('destination').trim(),
      method: formData.get('method')
    };

    if(tw.coordinates.latitude && tw.coordinates.longitude) {
      sendData.start_location = Object.values(tw.coordinates).join();
    }

    if(!sendData.start_location.length || !sendData.end_location.length) {
      alert('Please fill out all input fields to continue.');
    } else if(JSON.stringify(tw.collection) === JSON.stringify(sendData)) {
      tw.scrolly();
    } else {
      if(articles.length) {
        articles.remove();
      }

      submit.prop('disabled', true);

      tw.logo.addClass('loading');

      $.ajax({
        type: 'POST',
        url: 'https://us-central1-travelweather-1548474103293.cloudfunctions.net/travelweather-1',
        data: JSON.stringify(sendData),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        crossDomain: true,
        success: function(get) {
          var footer = $('main > footer');
          var template = $('body > template').html();

          tw.collection = sendData;

          $.each(get.hourly, function(index, hour) {
            var cloned = $(template);

            cloned.find('[data-fill]').each(function(index, item) {
              var item = $(item);
              var fill = item.data('fill');

              switch(fill) {
                case 'time':
                  item.text(hour.time);
                break;

                case 'timezone':
                  item.text(hour.timezone);
                break;

                case 'temperature':
                  if(hour.temp > 50) {
                    var label = item.prev('dt').find('label');

                    label.prev().prependTo(label.parent());
                  }

                  item.html(Math.round(hour.temp));
                break;

                case 'location':
                  item.text([
                    hour.city,
                    hour.state
                  ].join(', '));
                break;

                case 'distance':
                  item.text(hour.distance);
                break;
              }
            });

            cloned.find('[data-fill-icon]').attr('data-icon', [
              'weather',
              hour.icon
            ].join('/'));

            cloned.insertBefore(footer);
          });

          tw.mapicon();
          tw.maptime();
          tw.scrolly();

          submit.text('Reroute').prop('disabled', false);

          tw.logo.removeClass('loading');
        }
      });
    }

    event.preventDefault();
  }
});
