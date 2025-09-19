---
theme: default
background: https://source.unsplash.com/1920x1080/?church,faith
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  ## Seminary Lesson - [DATE]
  Weekly lesson for Seminary class
  Source materials available in ./materials/
drawings:
  persist: false
transition: slide-left
title: Seminary Lesson
mdc: true
---

# Seminary Lesson
## [DATE]

<div class="pt-12">
  <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover="bg-white bg-opacity-10">
    Press Space for next page <carbon:arrow-right class="inline"/>
  </span>
</div>

<div class="abs-br m-6 flex gap-2">
  <button @click="$slidev.nav.openInEditor()" title="Open in Editor" class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon:edit />
  </button>
  <a href="https://github.com/slidevjs/slidev" target="_blank" alt="GitHub"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
</div>

---
layout: default
---

# Welcome to Seminary

<div class="grid grid-cols-2 gap-4">

<div>

## Today's Focus
- **Scripture Study**: [Add your scripture reference]
- **Key Principle**: [Add the main principle]
- **Application**: [How students can apply this]

</div>

<div>

## Class Structure
1. **Opening Prayer** (2 min)
2. **QT Time** (10 min) - [Student Name]
3. **Scripture Study** (15 min)
4. **Discussion** (20 min)
5. **Application** (10 min)
6. **Closing Prayer** (3 min)

</div>

</div>

---
layout: section
---

# QT Time

<div class="text-center space-y-2">

### This Week's Leader: [Student Name]

#### Main Question
**[Student's main question from virtual lessons]**

### Light Bulb Moments

<div class="text-left space-y-1 text-sm">

• **[Student 1's Topic]**: [Their question or insight]  
  *[Their answer or explanation]*

• **[Student 2's Topic]**: [Their question or insight]  
  *[Their answer or explanation]*

• **[Student 3's Topic]**: [Their question or insight]  
  *[Their answer or explanation]*

</div>

<div class="flex justify-center space-x-4 mt-4">

<img src="./lessons/[YYYY-MM-DD]/materials/qt-time/meme1.png" class="h-32 w-auto rounded" />

<img src="./lessons/[YYYY-MM-DD]/materials/qt-time/meme2.png" class="h-32 w-auto rounded" />

</div>

</div>

---
layout: section
---

# Scripture Study

<div class="text-center">
  <h2 class="text-4xl font-bold mb-8">[Add Scripture Reference]</h2>
  <p class="text-xl text-gray-600">[Add key verse or passage]</p>
</div>

---
layout: two-cols
---

# Key Principles

::left::

## Principle 1
[Add your first key principle]

- Supporting point 1
- Supporting point 2
- Supporting point 3

::right::

## Principle 2
[Add your second key principle]

- Supporting point 1
- Supporting point 2
- Supporting point 3

---
layout: center
class: text-center
---

# Discussion Questions

<div class="space-y-4 text-left max-w-2xl mx-auto">

1. **How does this principle apply to your life today?**

2. **What challenges might you face in living this principle?**

3. **How can you help others understand this truth?**

4. **What specific action will you take this week?**

</div>

---
layout: section
---

# Application

<div class="grid grid-cols-1 md:grid-cols-2 gap-8">

<div>

## This Week's Challenge
[Add a specific challenge or goal for students]

</div>

<div>

## Personal Reflection
[Add a reflection question or journal prompt]

</div>

</div>

---
layout: center
class: text-center
---

# Closing

<div class="space-y-6">

## Key Takeaways
- [Takeaway 1]
- [Takeaway 2]
- [Takeaway 3]

## Next Week
[Preview of next week's lesson]

</div>

<div class="pt-8">
  <span class="text-lg">"And now, my sons, remember, remember that it is upon the rock of our Redeemer, who is Christ, the Son of God, that ye must build your foundation..."</span>
  <div class="text-sm text-gray-500 mt-2">- Helaman 5:12</div>
</div>

---
layout: end
---

# Thank You

<div class="text-center space-y-4">

## Questions?

Feel free to ask any questions about today's lesson.

## Next Class
[Add next class details]

</div>

<div class="abs-br m-6 text-sm text-gray-400">
  Seminary Lesson - [DATE]
</div>
