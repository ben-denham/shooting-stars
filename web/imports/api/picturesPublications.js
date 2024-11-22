import { Meteor } from 'meteor/meteor';

import { PicturesCollection } from '/imports/db/PicturesCollection';

Meteor.publish('pictures', async function publishPictures() {
  return await PicturesCollection.findAsync({}, {
    fields: {
      key: 1,
      timestamp: 1,
      pictureKey: 1,
    }
  });
});
