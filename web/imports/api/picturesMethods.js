import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';

import { PicturesCollection } from '/imports/db/PicturesCollection';

export const PICTURE_KEYS = [
  'mary',
  'joseph',
  'angel',
  'shepherd',
  'wisemen',
  'jesus',
  'star',
];

export const picturesMethods = {
  'pictures.setPicture'(pictureKey) {
    check(pictureKey, String);

    if (!PICTURE_KEYS.includes(pictureKey)) {
      throw new Meteor.Error('invalid-picture', 'Invalid picture');
    }

    const selector = {key: 'picture'};
    PicturesCollection.upsert(
      selector,
      {
        timestamp: (new Date()).getTime(),
        pictureKey: pictureKey,
        ...selector,
      }
    );
  },
};

Meteor.methods(picturesMethods);

