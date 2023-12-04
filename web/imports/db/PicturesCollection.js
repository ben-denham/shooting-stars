import { Mongo } from 'meteor/mongo';

export const PicturesCollection = new Mongo.Collection('pictures');

// Deny all client-side updates on the pictures collection
PicturesCollection.deny({
  insert() { return true; },
  update() { return true; },
  remove() { return true; },
});
