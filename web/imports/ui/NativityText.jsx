import React, { useState } from 'react';
import {createUseStyles} from 'react-jss';

const maryImage = '/images/pixel-art/mary.gif';
const josephImage = '/images/pixel-art/joseph.gif';
const angelImage = '/images/pixel-art/angel.gif';
const shepherdImage = '/images/pixel-art/shepherd.gif';
const wisemenImage = '/images/pixel-art/wisemen.gif';
const jesusImage = '/images/pixel-art/jesus.gif';
const starImage = '/images/pixel-art/star.gif';

const useStyles = createUseStyles({
  scripture: {
    textAlign: 'left',
    margin: '0 20px',
    '& p': {
      textIndent: '2em'
    },
  },
  verse: {
    verticalAlign: 'super',
    fontSize: '0.6em'
  },
  hightlightLink: {
    background: 'none',
    border: 'none',
    padding: 0,
    fontSize: '1.2em',
    fontWeight: 'bold',
    cursor: 'pointer',
    textDecoration: 'underline',
  },
});

export const NativityText = ({ onLinkClick }) => {
  const classes = useStyles();

  const pics = {
    mary: {key: 'mary', image: maryImage, color: '#57c1ff'},
    joseph: {key: 'joseph', image: josephImage, color: '#ff5656'},
    angel: {key: 'angel', image: angelImage, color: '#f7ff57'},
    shepherd: {key: 'shepherd', image: shepherdImage, color: '#57ff76'},
    wisemen: {key: 'wisemen', image: wisemenImage, color: '#b657ff'},
    jesus: {key: 'jesus', image: jesusImage, color: '#c78800'},
    star: {key: 'star', image: starImage, color: '#ffe500'},
  };

  const Link = ({ children, pic }) => {
    return (
      <button
        className={classes.hightlightLink}
        style={{color: pic.color}}
        onClick={() => onLinkClick(pic)}
      >
        {children}
      </button>
    );
  };

  return (
    <div className={classes.scripture}>
      <h2>Matthew 1:18-21</h2>
      <p>
        <span className={classes.verse}>18&nbsp;</span>Now the birth of <Link pic={pics.jesus}>Jesus Christ</Link> was
        like this: After his mother, <Link pic={pics.mary}>Mary</Link>, was engaged to <Link pic={pics.joseph}>Joseph</Link>, before
        they came together, she was found pregnant by the Holy
        Spirit. <span className={classes.verse}>19&nbsp;</span><Link pic={pics.joseph}>Joseph</Link>, her husband, being a
        righteous man, and not willing to make her a public example,
        intended to put her away secretly. <span className={classes.verse}>20&nbsp;</span>But
        when he thought about these things, behold, an <Link pic={pics.angel}>angel</Link> of the Lord
        appeared to him in a dream, saying, “<Link pic={pics.joseph}>Joseph</Link>, son of David, don’t
        be afraid to take to yourself <Link pic={pics.mary}>Mary</Link> as your wife, for that which is
        conceived in her is of the Holy Spirit. <span className={classes.verse}>21&nbsp;</span>She
        shall give birth to a son. You shall name him <Link pic={pics.jesus}>Jesus</Link>, for it is he
        who shall save his people from their sins.”
      </p>

      <h2>Luke 2:7-20</h2>
      <p>
        <span className={classes.verse}>7&nbsp;</span>She gave
        birth to her firstborn <Link pic={pics.jesus}>son</Link>. She wrapped him in bands of cloth and
        laid him in a feeding trough, because there was no room for them
        in the inn.
      </p>
      <p>
        <span className={classes.verse}>8&nbsp;</span>There were <Link pic={pics.shepherd}>shepherds</Link> in the same
        country staying in the field, and keeping watch by night over
        their flock. <span className={classes.verse}>9&nbsp;</span>Behold, an <Link pic={pics.angel}>angel</Link> of the
        Lord stood by them, and the glory of the Lord shone around them,
        and they were terrified. <span className={classes.verse}>10&nbsp;</span>The <Link pic={pics.angel}>angel</Link> said
        to them, “Don’t be afraid, for behold, I bring you good news
        of great joy which will be to all the
        people. <span className={classes.verse}>11&nbsp;</span>For there is born to you
        today, in David’s city, a Savior, who is Christ the
        Lord. <span className={classes.verse}>12&nbsp;</span>This is the sign to you: you
        will find a <Link pic={pics.jesus}>baby</Link> wrapped in strips of cloth, lying in a feeding
        trough.” <span className={classes.verse}>13&nbsp;</span>Suddenly, there was with
        the <Link pic={pics.angel}>angel</Link> a multitude of the heavenly army praising God and
        saying,<br/>
        <span className={classes.verse}>14&nbsp;</span>“Glory to God in the highest,<br/>
        on earth peace, good will toward men.”
      </p>
      <p>
        <span className={classes.verse}>15&nbsp;</span>When the <Link pic={pics.angel}>angels</Link> went away from them
        into the sky, the <Link pic={pics.shepherd}>shepherds</Link> said to one another, “Let’s go to
        Bethlehem, now, and see this thing that has happened, which the
        Lord has made known to us.” <span className={classes.verse}>16&nbsp;</span>They
        came with haste and found both <Link pic={pics.mary}>Mary</Link> and <Link pic={pics.joseph}>Joseph</Link>, and the <Link pic={pics.jesus}>baby</Link> was
        lying in the feeding trough. <span className={classes.verse}>17&nbsp;</span>When
        they saw it, they publicized widely the saying which was spoken to
        them about this <Link pic={pics.jesus}>child</Link>. <span className={classes.verse}>18&nbsp;</span>All who heard
        it wondered at the things which were spoken to them by
        the <Link pic={pics.shepherd}>shepherds</Link>. <span className={classes.verse}>19&nbsp;</span>But <Link pic={pics.mary}>Mary</Link> kept all these
        sayings, pondering them in her
        heart. <span className={classes.verse}>20&nbsp;</span>The <Link pic={pics.shepherd}>shepherds</Link> returned,
        glorifying and praising God for all the things
        that they had heard and seen, just as it was told them.
      </p>

      <h2>Matthew 2:1-2,11</h2>
      <p>
        <span className={classes.verse}>1&nbsp;</span>Now when <Link pic={pics.jesus}>Jesus</Link> was born in Bethlehem
        of Judea in the days of King Herod, behold, <Link pic={pics.wisemen}>wise men</Link> from the east
        came to Jerusalem, saying, <span className={classes.verse}>2&nbsp;</span>“Where is
        he who is born King of the Jews? For we saw his <Link pic={pics.star}>star</Link> in the east,
        and have come to worship him.”
        &hellip;&nbsp;
        <span className={classes.verse}>11&nbsp;</span>They came into the house and
        saw the young <Link pic={pics.jesus}>child</Link> with <Link pic={pics.mary}>Mary</Link>, his mother, and they fell down and
        worshiped him. Opening their treasures, they offered to him gifts:
        gold, frankincense, and myrrh.
      </p>
    </div>
  );
};
