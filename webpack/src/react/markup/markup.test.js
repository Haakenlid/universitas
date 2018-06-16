import { parseText, renderText } from './index.js'

const cases = {
  title: [
    '@tit: Hello World',
    [{ type: 'blockTag', tag: 'tit', children: ['Hello World'] }],
  ],
  paragraph: [
    'Hello World',
    [{ type: 'paragraph', children: ['Hello World'] }],
  ],
  quote: [
    '@sitat: Hello\n@txt: World',
    [{ type: 'pullquote', children: [{ type: 'paragraph' }, { tag: 'txt' }] }],
  ],
  quotesplit: [
    '@sitat: Hello\n\n@sitatbyline: World',
    [{ type: 'pullquote', children: ['Hello'] }, { type: 'blockTag' }],
  ],
  faktaboks: [
    '@fakta: her er fakta\n# foo1\n# foo2\n\n@mt: mellomtittel',
    [{ type: 'facts', children: [{}, {}, {}] }, { tag: 'mt' }],
  ],
  place: ['[[ faktaboks 1 ]]', [{ type: 'place', name: 'faktaboks 1' }]],
  link: ['[hi]', [{ children: [{ children: ['hi'], ref: 'hi' }] }]],
  'full link': [
    '[hello](//world.com)',
    [{ children: [{ type: 'link', children: ['hello'], ref: '//world.com' }] }],
  ],
  'partial link': [
    '[hello](//world',
    [{ children: [{ children: ['hello'], ref: 'hello' }, '(//world'] }],
  ],
  'partial link 2': ['hello [world', [{ children: ['hello ', {}, 'world'] }]],
}

describe('parseText', () => {
  for (const c in cases)
    test(c, () => expect(parseText(cases[c][0])).toMatchObject(cases[c][1]))
})

describe('renderText', () => {
  const reverse = R.pipe(parseText, renderText)

  for (const c in cases)
    test(c, () => expect(reverse(cases[c][0])).toEqual(cases[c][0]))

  test('cleanup after', () => {
    expect(reverse('hello _world_, [link]')).toEqual('hello _world_, [link]')
    expect(reverse('-hi \n@mt:- hi. -hi!')).toEqual('– hi\n\n@mt: – hi. – hi!')
    expect(reverse('"hello "world""')).toEqual('«hello «world»»')
    expect(reverse('"hello" "world"')).toEqual('«hello» «world»')
  })
})
