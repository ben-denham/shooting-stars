import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { LightsCollection, COLOUR_MODES, ANIMATIONS } from '/imports/db/LightsCollection';

export const lightsMethods = {
  async 'lights.setColourMode'(lightId, colourMode) {
    check(lightId, String);
    check(colourMode, String);

    if (!COLOUR_MODES.includes(colourMode)) {
      throw new Meteor.Error('invalid-colour-mode', 'Invalid colour mode');
    }

    await LightsCollection.updateAsync(lightId, {
      $set: { colourMode }
    });
  },
  async 'lights.setColourHue'(lightId, colourHue) {
    check(lightId, String);
    check(colourHue, Number);

    if (colourHue < 0 || colourHue > 1) {
      throw new Meteor.Error('invalid-colour-hue', 'Hue must be between 0 and 1');
    }

    await LightsCollection.updateAsync(lightId, {
      $set: { colourHue }
    });
  },
  async 'lights.setColourSaturation'(lightId, colourSaturation) {
    check(lightId, String);
    check(colourSaturation, Number);

    if (colourSaturation < 0 || colourSaturation > 1) {
      throw new Meteor.Error('invalid-colour-saturation', 'Saturation must be between 0 and 1');
    }

    await LightsCollection.updateAsync(lightId, {
      $set: { colourSaturation }
    });
  },
  async 'lights.setAnimation'(lightId, animation) {
    check(lightId, String);
    check(animation, String);

    if (!ANIMATIONS.includes(animation)) {
      throw new Meteor.Error('invalid-animation', 'Invalid animation');
    }

    await LightsCollection.updateAsync(lightId, {
      $set: { animation }
    });
  }
};

Meteor.methods(lightsMethods);
