import { Mongo } from 'meteor/mongo';

export const LIGHT_COUNT = 10;
export const COLOUR_MODES = [
  'white',
  'colour',
  'rainbow',
  'gradual',
];
export const ANIMATIONS = [
  'static',
  'twinkle',
  'rain',
  'wave',
];

export const LightsCollection = new Mongo.Collection('lights');

// Deny all client-side updates on the Lists collection
LightsCollection.deny({
  insert() { return true; },
  update() { return true; },
  remove() { return true; },
});
