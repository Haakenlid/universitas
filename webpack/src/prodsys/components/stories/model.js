import { modelActions, modelSelectors } from 'ducks/basemodel'
import { fieldFactory } from 'components/ModelField'

export const MODEL = 'stories'
export const actions = modelActions(MODEL)
export const selectors = modelSelectors(MODEL)

export const fields = {
  title: { label: 'tittel', type: 'string' },
  lede: { label: 'ingress', type: 'string' },
  kicker: { label: 'stikktittel', type: 'string' },
  working_title: { label: 'arbeidstittel', type: 'string' },
  created: { label: 'opprettet', type: 'datetime' },
  modified: { label: 'endret', type: 'datetime' },
  story_type_name: { label: 'artikkeltype', type: 'string' },
  bodytext_markup: { label: 'tekst', type: 'text' },
  byline_set: { label: 'bylines', type: 'count' },
  images: { label: 'foto', type: 'count' },
  publication_status: {
    label: 'status',
    type: 'select',
    options: [
      {
        label: 'Prod',
        options: [
          { value: 3, label: 'Journalist' },
          { value: 4, label: 'Mellomleder' },
          { value: 5, label: 'Redaktør' },
        ],
      },
      {
        label: 'Desk',
        options: [
          { value: 6, label: 'Til Desken' },
          { value: 7, label: 'På Desken' },
        ],
      },
      {
        label: 'Nett',
        options: [
          { value: 9, label: 'Nettredaktør' },
          { value: 10, label: 'På nett' },
          { value: 11, label: 'På nett *' },
        ],
      },
      {
        label: 'Etc',
        options: [
          { value: 0, label: 'Skisse' },
          { value: 100, label: 'Mal' },
          { value: 15, label: 'Slettet' },
        ],
      },
    ],
  },
  story_type: { type: 'select', label: 'artikkeltype', to: 'storytypes' },
}

export const Field = fieldFactory(MODEL, fields)
