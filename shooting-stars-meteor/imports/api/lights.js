import { Mongo } from 'meteor/mongo';

export const LIGHT_COUNT = 10;

export const LightsCollection = new Mongo.Collection('lights');
