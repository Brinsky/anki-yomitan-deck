# Mining Deck Template
A basic Anki deck template for use with Yomitan. Forked from https://github.com/friedrich-de/Basic-Mining-Deck.

## Yomichan Fields
| Anki Field    | Yomitan Template        | 
|---------------|--------------------------|
| Word          | {expression}             | 
| Reading       | {reading}                |
| Glossary      | {glossary-no-dictionary} |
| Sentence      | {clipboard-text}         |
| Picture       |                          |
| Audio         | {audio}                  |
| SentenceAudio |                          |
| Graph         | {pitch-accent-graphs}    |
| Hint          |                          |

## How to update
Open a card with the corresponding template in Anki. 

Then `Edit` > `Cards...`

Go to repository directory AnkiFields and copy the text from `front.html` to `Front`,
from `back.html` to `Back` and from `styling.css` to `Styling`.

If you changed field names to something else, you will have to make changes to the
corresponding text in the files.