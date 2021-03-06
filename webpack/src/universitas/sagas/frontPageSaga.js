import {
  takeLatest,
  takeEvery,
  call,
  put,
  select,
  fork,
  delay,
} from 'redux-saga/effects'
import { apiList, apiGet } from 'services/api'
import {
  STORY_REQUESTED,
  STORIES_REQUESTED,
  storyFetching,
  storiesFetching,
  storyFetched,
  storiesFetched,
  getStory,
  getStoryIds,
} from 'ducks/publicstory'
import { SITE_REQUESTED, siteFetched } from 'ducks/site'
import { ISSUES_REQUESTED, issuesFetched } from 'ducks/issues'
import {
  FEED_REQUESTED,
  SEARCH,
  feedFetched,
  searchFetched,
  getFeedQuery,
} from 'ducks/newsFeed'

import * as adverts from 'ducks/adverts'

const DEBOUNCE = 300 // ms debounce

const routeAction = R.propSatisfies(R.test(/^router/), 'type')

export default function* rootSaga() {
  yield fork(pageView) // initial page view for analytics
  yield takeLatest(FEED_REQUESTED, fetchFeed)
  yield takeLatest(SITE_REQUESTED, fetchSite)
  yield takeLatest(ISSUES_REQUESTED, fetchIssues)
  yield takeLatest(SEARCH, fetchSearch)
  yield takeEvery(STORY_REQUESTED, fetchStory)
  yield takeEvery(STORIES_REQUESTED, fetchStories)
  yield takeLatest(routeAction, pageView)
  yield takeLatest(adverts.ADVERTS_REQUESTED, fetchAdverts)
}

const handleError = error => console.error(error)

function* fetchAdverts(action) {
  // fetch Qmedia ads
  yield put(adverts.advertsFetching())
  const { response, error } = yield call(apiGet, 'adverts', 'qmedia')
  if (response) yield put(adverts.advertsFetchSuccess(response))
  else yield call(handleError, error)
}

function* fetchStories(action) {
  const fetched = yield select(getStoryIds)
  const ids = R.difference(R.map(parseFloat, action.payload.ids), fetched)
  if (R.isEmpty(ids)) return
  yield put(storiesFetching(ids))
  const { response, error } = yield call(apiList, 'publicstories', {
    id__in: ids,
  })
  if (response) yield put(storiesFetched(response))
  else yield call(handleError, error)
}

function* fetchStory(action) {
  const { id, prefetch } = action.payload
  const story = yield select(getStory)
  if (prefetch && (story.fetching || story.id)) return
  yield put(storyFetching(id))
  const { response, error } = yield call(apiGet, 'publicstories', id)
  if (response) yield put(storyFetched(response))
  else {
    yield call(handleError, error)
    if (error.HTTPstatus) yield put(storyFetched({ id, ...error }))
  }
}

function* fetchSearch(action) {
  const params = yield select(getFeedQuery)
  const { search } = params
  if (!search) yield put(searchFetched({ results: [], next: false }))
  else {
    yield delay(search.length > 3 ? DEBOUNCE : DEBOUNCE * 3)
    const { response, error } = yield call(apiList, 'frontpage', params)
    if (response) yield put(searchFetched(response))
    else yield call(handleError, error)
  }
}

function* fetchFeed(action) {
  let params = yield select(getFeedQuery)
  params = R.merge(params, action.payload)

  if (!R.isEmpty(params)) yield delay(DEBOUNCE)
  const { response, error } = yield call(apiList, 'frontpage', params)
  if (response) yield put(feedFetched(response))
  else yield call(handleError, error)
}

function* fetchSite(action) {
  const { response, error } = yield call(apiList, 'site', {})
  if (response) yield put(siteFetched(response))
  else yield call(handleError, error)
}

function* fetchIssues(action) {
  const { response, error } = yield call(apiList, 'issues', {})
  if (response) yield put(issuesFetched(response))
  else yield call(handleError, error)
}

const googleAnalyticsPageView = action => {
  // register a new page view with google analytics
  const document = global.document
  const ga = global.ga
  if (!document) return
  const viewData = {
    page: document.location.pathname,
    title: R.replace(/ *\|.*$/, '', document.title),
  }
  if (ga) {
    ga('set', viewData)
    ga('send', 'pageview')
  } // else console.log('debug: google analytics pageview', viewData)
}

function* pageView(action) {
  yield delay(500) // debounce
  yield call(googleAnalyticsPageView, action)
}
