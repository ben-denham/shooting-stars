import { Meteor } from 'meteor/meteor';

import { PicturesCollection } from '/imports/db/PicturesCollection';

Meteor.publish('pictures', function publishPictures() {
  return PicturesCollection.find({}, {
    fields: {
      key: 1,
      timestamp: 1,
      pictureKey: 1,
    }
  });
});
