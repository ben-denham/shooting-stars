import { Mongo } from 'meteor/mongo';

export const PresenceCollection = new Mongo.Collection('presence');

// Deny all client-side updates on the presence collection
PresenceCollection.deny({
  insert() { return true; },
  update() { return true; },
  remove() { return true; },
});
