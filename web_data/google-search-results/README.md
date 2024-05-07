# google-search-results

This is a clone of the Google search results page. The goal was to have something indistinguishable from the originial for the keenest of eyes. To accomplish that, I would inspect the original source code to fine-tune the styling accordingly. (Is that a crime?)  

The page was divided into three sections:

1. The `header`, which contains the search field and navigation links
2. The `main`, which contains the results
3. The `footer`, which contains some links

The `header` contains the Google image, the search field, the "apps" icon and the
"Sign in" button inside a **Flexbox container**. With **Flexbox container**, I found it easier to keep everything aligned and to position some elements to the 
right. For instance, the "apps" icon and the "Sign in" button, and the "Settings"
and "Tools" links. You just set the `margin-left` property to `auto` for the
element that you want to position to the right. But notice that there are other ways
to achieve the same result, like floating the element or using
the `position` property. However, Flexbox brings flexibility and responsiveness to the table.

In the `main` section, the results are items of an unordered list. The same with "related searchs".  
For that "Goooooooooogle" at the bottom, I found it
easier to just use a `table` with one row. Each letter is an
image inside a cell of the table, except the "gle >", which is just a image
in a cell.

The `footer` contains only a `div` with the name of the country and an unordered list with
a few links.

As a sidenote, I had issues with the shadow effect of the `form`
element. The `form` contains two children: an `input` for the search field and a
`button` to submit. When the `input` (the search field) was focused, I wanted the
shadow to change for the whole `form` element. But here is the problem: when you
focus an element, how do you select its parent to apply a property to it
(`box-shadow`, in this case)? Well, with pure CSS, the only way, apparently, is
by using the `:has()` pseudo-class. But, as of 2018, this is experimental and [not
supported by any browser](https://caniuse.com/#feat=css-has). This limitation is
well know, as can be seen [here](https://stackoverflow.com/questions/2212583/affecting-parent-element-of-focusd-element-pure-csshtml-preferred#2212935), [here](https://stackoverflow.com/questions/1014861/is-there-a-css-parent-selector?noredirect=1&lq=1) and [here](https://en.wikipedia.org/wiki/Cascading_Style_Sheets#Limitations). Then, I resorted to JavaScript to solve this problem. When you focus the search field (`input` element), a function is called via the `addEventListener()` method. This function sets the `box-shadow` property of the `form` element via the `setAttribute()` method. When the search field loses focus, another function is called to set the `box-shadow` property of the `form` back to normal. But now you have a new problem. The `box-shadow` property
applied by the script is *inline* style and overrides the `box-shadow` property
applied when the `form` is hovered. Now, the shadow doesn't change if the `form` is hovered. To bypass this, I used an `!important` declaration to prioritize the `box-shadow` property in the `form:hover` selector. Very hackish and inelegant, I know. But hey, it works! (Please, feel free to open a pull request in case you have a better solution and also if your time is valuable enough to be spent in such an important problem.)

Another sidenote. When testing the page in Chrome for Android, the headings and paragraphs inside `#results` were too big. I
found out that this was caused by a "feature" in some mobile browsers called
*Font Boosting*. It's described
[here](https://bugs.webkit.org/show_bug.cgi?id=84186). According to [this
answer](https://bugs.webkit.org/show_bug.cgi?id=84186#c17), the only side-effect-free way to disable *Font Boosting* is setting the CSS property `max-height` to any fixed height greater than the actual height for the block that contains the text (I just set to `1000000px`). Setting the `max-height` for all elements
inside `main` (`main * {max-height: 1000000px;}`) solved the problem. This is also hackish and all, but I just wanted the fonts rendering the way they should.

---

From The Odin Project's [curriculum](http://www.theodinproject.com/courses/web-development-101/lessons/html-css).
