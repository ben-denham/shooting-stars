import { Mongo } from 'meteor/mongo';

export const BlocksStatesCollection = new Mongo.Collection('blocksStates');

// Deny all client-side updates on the BlocksStates collection
BlocksStatesCollection.deny({
  insert() { return true; },
  update() { return true; },
  remove() { return true; },
});
