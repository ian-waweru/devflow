import api from '../api/axios';

// DRF pagination caps each page at PAGE_SIZE (20) results. Every list in
// this app previously only ever read the first page (response.data.results),
// silently hiding anything beyond it with no indication data was missing.
// This follows `next` (a full URL) until exhausted and returns every result.
export const fetchAllPages = async (initialResponse) => {
  let results = [...initialResponse.data.results];
  let nextUrl = initialResponse.data.next;

  while (nextUrl) {
    const response = await api.get(nextUrl);
    results = results.concat(response.data.results);
    nextUrl = response.data.next;
  }

  return results;
};