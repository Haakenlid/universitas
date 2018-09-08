import { Field } from './model.js'

const StoryImageForm = ({ pk }) => (
  <form className="StoryImageForm">
    <Field pk={pk} name="caption" editable />
    <Field pk={pk} name="ordering" editable />
    <Field pk={pk} name="placement" editable />
    <Field pk={pk} name="size" editable />
    <Field pk={pk} name="aspect_ratio" editable />
    <Field pk={pk} name="creditline" editable />
  </form>
)

export default StoryImageForm
