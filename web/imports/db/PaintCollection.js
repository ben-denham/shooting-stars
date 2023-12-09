import { Mongo } from 'meteor/mongo';

export const PaintCollection = new Mongo.Collection('paint');

// Deny all client-side updates on the pictures collection
PaintCollection.deny({
  insert() { return true; },
  update() { return true; },
  remove() { return true; },
});
