import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { LightsCollection, COLOUR_MODES } from '/imports/db/LightsCollection';

export const lightsMethods = {
  'lights.setColourMode'(lightId, colourMode) {
    check(lightId, String);
    check(colourMode, String);

    if (!COLOUR_MODES.includes(colourMode)) {
      throw new Meteor.Error('invalid-colour-mode', 'Invalid colour mode');
    }

    LightsCollection.update(lightId, {
      $set: { colourMode }
    });
  }
};

Meteor.methods(lightsMethods);
