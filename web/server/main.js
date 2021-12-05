import { Meteor } from 'meteor/meteor';
import { DDPRateLimiter } from 'meteor/ddp-rate-limiter';
import { LightsCollection, LIGHT_COUNT } from '/imports/db/LightsCollection';
import { lightsMethods } from '/imports/api/lightsMethods';
import '/imports/api/lightsPublications';

Meteor.startup(() => {
  // Initialise lights.
  for (let idx = 0; idx < LIGHT_COUNT; idx++) {
    if (!LightsCollection.findOne({idx})) {
      LightsCollection.insert({
        idx,
        colourMode: 'white',
        colourHue: 0.0,
        colourSaturation: 1.0,
        animation: 'static',
      });
    }
  }
});


DDPRateLimiter.addRule(
  {
    name(name) {
      return [
        // Methods
        ...Object.keys(lightsMethods),
        // Publications
        'lights'
      ].includes(name);
    },
    // Rate limit per connection ID
    connectionId() { return true; }
  },
  // Max 10 requests every second.
  10, 1000
);
