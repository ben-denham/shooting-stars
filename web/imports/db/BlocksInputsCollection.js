import { Mongo } from 'meteor/mongo';

export const BlocksInputsCollection = new Mongo.Collection('blocksInputs');

// Deny all client-side updates on the blocksInputs collection
BlocksInputsCollection.deny({
  insert() { return true; },
  update() { return true; },
  remove() { return true; },
});
